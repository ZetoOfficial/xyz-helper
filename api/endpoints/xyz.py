from fastapi import APIRouter
from fastapi import Request, HTTPException

from core.database import SessionNotFound
from use_cases.elbow_rule_graphic import ElbowRuleGraphic, ElbowRuleGraphicRequest, ElbowRuleGraphicResponse
from use_cases.export import Export, ExportRequest, ExportResponse
from use_cases.generate_image import GenerateImage, GenerateImageRequest, GenerateImageResponse
from use_cases.load_file import LoadFile, LoadFileRequest, LoadFileResponse, FileNotFoundException, FileNotAbsolute
from use_cases.show_image import ShowImage, ShowImageRequest, ShowImageResponse
from use_cases.upload_file import UploadFile, UploadFileResponse

router = APIRouter()


@router.post('/upload_file', response_model=UploadFileResponse)
async def upload_file(request: Request):
    return UploadFile().execute(request)


@router.post('/load_file', response_model=LoadFileResponse)
async def load_file(request: LoadFileRequest):
    try:
        return await LoadFile().execute(request)
    except FileNotAbsolute:
        raise HTTPException(status_code=400, detail='File not absolute')
    except FileNotFoundException:
        raise HTTPException(status_code=400, detail='File not found')


@router.post('/export', response_model=ExportResponse)
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
