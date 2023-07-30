from pydantic import BaseConfig, BaseModel


class Storage(BaseModel):
    storage_path: str
    base_url: str


class Database(BaseModel):
    collection: str


class Settings(BaseConfig):
    BASE_URL: str = '/api'

    STORAGE: Storage
    DATABASE: Database
