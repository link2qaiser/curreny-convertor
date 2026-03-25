
from fastapi import APIRouter, Depends
from app.utils.security import verify_api_key
from .service import get_from_s3
from .schema import CurrencyURLResponse, ErrorDetail

router = APIRouter()


@router.get(
    "/currency",
    response_model=CurrencyURLResponse,
    status_code=200,
    summary="Get latest currency rates URL",
    description="Returns a pre-signed S3 URL (valid 24 hours) to download the latest currency rates JSON file containing 150+ fiat currencies and top 50 cryptocurrencies.",
    responses={
        200: {"model": CurrencyURLResponse, "description": "Pre-signed download URL with expiry timestamp"},
        401: {"model": ErrorDetail, "description": "Invalid API key — check the X-API-Key header value"},
        422: {"description": "X-API-Key header is missing from the request"},
        500: {"model": ErrorDetail, "description": "Failed to generate the download URL due to a storage service error"},
    },
)
async def get_currency_json_url(_: str = Depends(verify_api_key)):
    return await get_from_s3()