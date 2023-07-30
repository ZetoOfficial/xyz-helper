import os

from fastapi import Request, HTTPException, status
from pydantic import BaseModel
from starlette.requests import ClientDisconnect
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget

from core.database import memory_database
from utils.hash_generator import FileHashGenerator


class UploadFileResponse(BaseModel):
    session_id: str


class UploadFile:
    @staticmethod
    async def execute(request: Request) -> UploadFileResponse:
        filename = request.headers.get('Filename')

        if not filename:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Filename header is missing')
        try:
            filepath = os.path.join('static/', os.path.basename(filename))
            file_ = FileTarget(filepath)
            data = ValueTarget()
            parser = StreamingFormDataParser(headers=request.headers)
            parser.register('file', file_)
            parser.register('data', data)

            async for chunk in request.stream():
                parser.data_received(chunk)
        except ClientDisconnect:
            raise HTTPException(500, detail='Client disconnected')
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='There was an error uploading the file'
            )

        if not file_.multipart_filename:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='File is missing')

        session_id = FileHashGenerator().generate_session_id()

        if (result := (await memory_database.find_by_field("filepath", filepath))) is not None:
            return UploadFileResponse(session_id=result)

        await memory_database.set(session_id, {"filepath": filepath})

        return UploadFileResponse(session_id=session_id)
