import os

import aioredis
from pydantic import BaseModel

from utils.hash_generator import FileHashGenerator


class LoadFileRequest(BaseModel):
    xyz_path: str


class LoadFileResponse(BaseModel):
    session_id: str


class FileNotFoundException(Exception):
    pass


class LoadFile:
    @staticmethod
    def _validate(filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundException

    async def execute(self, request: LoadFileRequest, redis: aioredis.Redis) -> LoadFileResponse:
        self._validate(request.xyz_path)

        hash_generator = FileHashGenerator()
        session_id = hash_generator.generate_session_id()

        data = {
            "md5_hash": hash_generator.file_md5_hash(request.xyz_path),
            "filepath": request.xyz_path,
        }
        await redis.hmset(session_id, data)
        await redis.expire(name=session_id, time=60 * 60 * 2)

        return LoadFileResponse(session_id=session_id)
