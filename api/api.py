from fastapi import APIRouter

from .endpoints import xyz

router = APIRouter()
router.include_router(xyz.router)
