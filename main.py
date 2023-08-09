import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from api.api import router as api_router

BASE_URL = '/api'

app = FastAPI(
    title='XYZ Helper',
    openapi_url=f'{BASE_URL}/openapi.json',
    docs_url=f'{BASE_URL}/docs',
    redoc_url=f'{BASE_URL}/redoc',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_event_handler("startup", connect_to_mongo)
# app.add_event_handler("shutdown", close_mongo_connection)
STATIC_DIR = 'static'

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
app.mount('/static', StaticFiles(directory=STATIC_DIR), name=STATIC_DIR)
app.include_router(api_router, prefix=BASE_URL)
