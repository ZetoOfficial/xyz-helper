import aioredis
from pydantic import BaseModel


class ExportRequest(BaseModel):
    session_id: str
    indexes: list[int]


class ExportResponse(BaseModel):
    session_id: str
    filepath: str


class Export:
    @staticmethod
    async def execute(request: ExportRequest, redis: aioredis.Redis) -> ExportResponse:
        pass
