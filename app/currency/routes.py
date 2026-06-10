
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.security import verify_api_key
from app.utils.database import async_session
from .service import get_from_s3, get_currency_history
from .schema import (
    CurrencyURLResponse,
    CurrencyHistoryResponse,
    CurrencyCode,
    HistoryRange,
    ErrorDetail,
)

router = APIRouter()


async def _db():
    async with async_session() as session:
        yield session


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


@router.get(
    "/currency/history",
    response_model=CurrencyHistoryResponse,
    status_code=200,
    summary="Get historical exchange-rate series for a currency pair",
    description=(
        "Returns a time-ordered series of `base → quote` exchange rates over the "
        "requested range, plus summary stats (current / change / high / low). "
        "Granularity is chosen automatically per range: hourly for 1D/1W, daily "
        "for 1M/3M/1Y, weekly for 5Y, monthly for 10Y."
    ),
    responses={
        200: {"model": CurrencyHistoryResponse},
        400: {"model": ErrorDetail, "description": "Unknown base or quote currency code"},
        401: {"model": ErrorDetail, "description": "Invalid API key"},
        422: {"description": "Missing or malformed query params"},
    },
)
async def get_currency_history_endpoint(
    base: CurrencyCode = Query(..., description="Base currency code, e.g. EUR"),
    quote: CurrencyCode = Query(..., description="Quote currency code, e.g. AED"),
    range: HistoryRange = Query(HistoryRange.M1, description="Time range window"),
    db: AsyncSession = Depends(_db),
    _: str = Depends(verify_api_key),
):
    return await get_currency_history(db=db, base=base.value, quote=quote.value, range_=range)
