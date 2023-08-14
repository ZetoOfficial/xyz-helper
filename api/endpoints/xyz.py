import os

import streaming_form_data
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from starlette.requests import ClientDisconnect
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from streaming_form_data.validators import MaxSizeValidator

from core.database import SessionNotFound, memory_database
from use_cases.elbow_rule_graphic import ElbowRuleGraphic, ElbowRuleGraphicRequest, ElbowRuleGraphicResponse
from use_cases.export import Export, ExportRequest
from use_cases.generate_image import GenerateImage, GenerateImageRequest, GenerateImageResponse
from use_cases.load_file import FileNotAbsolute, FileNotFoundException, LoadFile, LoadFileRequest, LoadFileResponse
from use_cases.show_image import ShowImage, ShowImageRequest, ShowImageResponse
from use_cases.upload_file import (
    MAX_FILE_SIZE,
    MAX_REQUEST_BODY_SIZE,
    MaxBodySizeException,
    MaxBodySizeValidator,
    UploadFileResponse,
)
from utils.hash_generator import FileHashGenerator

router = APIRouter()


@router.post('/upload_file', response_model=UploadFileResponse)
async def upload_file(request: Request):
    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)
    filename = request.headers.get('Filename')

    if not filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Filename header is missing')
    try:
        filepath = os.path.join('static', os.path.basename(filename))
        file_ = FileTarget(filepath, validator=MaxSizeValidator(MAX_FILE_SIZE))
        data = ValueTarget()
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register('file', file_)
        parser.register('data', data)

        async for chunk in request.stream():
            body_validator(chunk)
            parser.data_received(chunk)

    except ClientDisconnect:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Client disconnected')
    except MaxBodySizeException as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f'Maximum request body size limit ({MAX_REQUEST_BODY_SIZE} bytes) exceeded ({e.body_len} bytes read)',
        )
    except streaming_form_data.validators.ValidationError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f'Maximum file size limit ({MAX_FILE_SIZE} bytes) exceeded',
        )
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


@router.post('/load_file', response_model=LoadFileResponse)
async def load_file(request: LoadFileRequest):
    try:
        return await LoadFile().execute(request)
    except FileNotAbsolute:
        raise HTTPException(status_code=400, detail='File not absolute')
    except FileNotFoundException:
        raise HTTPException(status_code=400, detail='File not found')


@router.post('/export', response_class=StreamingResponse)
async def export(request: ExportRequest):
    try:
        return await Export().execute(request)
    except SessionNotFound:
        raise HTTPException(status_code=400, detail='Session not found')


@router.post('/elbow_rule_graphic', response_model=ElbowRuleGraphicResponse)
async def elbow_rule_graphic(request: ElbowRuleGraphicRequest):
    try:
        return await ElbowRuleGraphic().execute(request)
    except SessionNotFound:
        raise HTTPException(status_code=400, detail='Session not found')


@router.post('/generate_image', response_model=GenerateImageResponse)
async def generate_image(request: GenerateImageRequest):
    try:
        return await GenerateImage().execute(request)
    except SessionNotFound:
        raise HTTPException(status_code=400, detail='Session not found')


@router.post('/show_image', response_model=ShowImageResponse)
async def show_image(request: ShowImageRequest):
    try:
        return await ShowImage().execute(request)
    except SessionNotFound:
        raise HTTPException(status_code=400, detail='Session not found')
