from pathlib import Path

from pydantic import BaseModel

from core.database import memory_database
from utils.hash_generator import FileHashGenerator


class LoadFileRequest(BaseModel):
    xyz_path: str


class LoadFileResponse(BaseModel):
    session_id: str


class FileNotFoundException(Exception):
    pass


class FileNotAbsolute(Exception):
    pass


class LoadFile:
    @staticmethod
    def _validate(filepath: str):
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundException
        if not path.is_absolute():
            raise FileNotAbsolute

    async def execute(self, request: LoadFileRequest) -> LoadFileResponse:
        self._validate(request.xyz_path)

        hash_generator = FileHashGenerator()

        session_id = hash_generator.generate_session_id()
        data = {"filepath": request.xyz_path}

        if (result := (await memory_database.find_by_field("filepath", data["filepath"]))) is not None:
            return LoadFileResponse(session_id=result)

        await memory_database.set(session_id, data)

        return LoadFileResponse(session_id=session_id)
