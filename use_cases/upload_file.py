from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    session_id: str


MAX_FILE_SIZE = 1024 * 1024 * 1024 * 10  # = 4GB
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024


class MaxBodySizeException(Exception):
    def __init__(self, body_len: str):
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=self.body_len)
