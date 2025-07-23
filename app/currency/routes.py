
from fastapi import APIRouter, Depends
from app.utils.security import verify_api_key
from .service import get_from_s3
router = APIRouter()


@router.get("/currency")
async def get_currency_json_url(_: str = Depends(verify_api_key)):
    return await get_from_s3()