import aioredis
from fastapi import Depends, FastAPI, HTTPException

from settings import get_redis_pool
from use_cases.elbow_rule_graphic import ElbowRuleGraphic, ElbowRuleGraphicRequest, ElbowRuleGraphicResponse
from use_cases.export import Export, ExportRequest, ExportResponse
from use_cases.generate_image import GenerateImage, GenerateImageRequest, GenerateImageResponse
from use_cases.load_file import FileNotFoundException, LoadFile, LoadFileRequest, LoadFileResponse
from use_cases.show_image import ShowImage, ShowImageRequest, ShowImageResponse

app = FastAPI(title="XYZ Helper")


@app.post('/load_file', response_model=LoadFileResponse)
async def load_file(request: LoadFileRequest, redis: aioredis.Redis = Depends(get_redis_pool)):
    try:
        return await LoadFile().execute(request, redis)
    except FileNotFoundException:
        return HTTPException(status_code=400, detail="File not found")


@app.post('/export', response_model=ExportResponse)
async def export(request: ExportRequest, redis: aioredis.Redis = Depends(get_redis_pool)):
    return await Export().execute(request, redis)


@app.post('/elbow_rule_graphic', response_model=ElbowRuleGraphicResponse)
async def elbow_rule_graphic(request: ElbowRuleGraphicRequest, redis: aioredis.Redis = Depends(get_redis_pool)):
    return await ElbowRuleGraphic().execute(request, redis)


@app.post('/generate_image', response_model=GenerateImageResponse)
async def generate_image(request: GenerateImageRequest, redis: aioredis.Redis = Depends(get_redis_pool)):
    return await GenerateImage().execute(request, redis)


@app.post('/show_image', response_model=ShowImageResponse)
async def show_image(request: ShowImageRequest, redis: aioredis.Redis = Depends(get_redis_pool)):
    return await ShowImage().execute(request, redis)
