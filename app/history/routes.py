from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.security import verify_api_key
from app.utils.database import async_session
from .service import get_currency_history
from .schema import (
    CurrencyHistoryResponse,
    HistoryRange,
    HistoryErrorDetail,
)

router = APIRouter(prefix="/history", tags=["history"])


async def _db():
    async with async_session() as session:
        yield session


@router.get(
    "",
    response_model=CurrencyHistoryResponse,
    status_code=200,
    summary="Get historical exchange-rate series for a currency pair",
    description=(
        "Returns a time-ordered series of `base_currency -> quote_currency` "
        "exchange rates over the requested range, plus summary stats "
        "(starting_rate, current_rate, highest_rate, lowest_rate, "
        "absolute_change, percent_change, direction) and the window's "
        "start_date / today_date.\n\n"
        "Spacing between points is chosen automatically: hourly for 1D/1W, "
        "daily for 1M/3M/6M/1Y, weekly for 3Y/5Y, monthly for 10Y. "
        "For ALL, spacing auto-scales to whatever data exists."
    ),
    responses={
        200: {"model": CurrencyHistoryResponse},
        400: {"model": HistoryErrorDetail, "description": "Unknown base or quote currency code"},
        401: {"model": HistoryErrorDetail, "description": "Invalid API key"},
        422: {"description": "Missing or malformed query params"},
    },
)
async def get_currency_history_endpoint(
    base_currency: str = Query(
        ...,
        min_length=3,
        max_length=5,
        example="EUR",
        description="Currency you are converting FROM (e.g. EUR, USD, BTC).",
    ),
    quote_currency: str = Query(
        ...,
        min_length=3,
        max_length=5,
        example="AED",
        description="Currency you are converting TO (e.g. AED, PKR, INR).",
    ),
    range: HistoryRange = Query(
        HistoryRange.ONE_MONTH, description="Time range window",
    ),
    db: AsyncSession = Depends(_db),
    _: str = Depends(verify_api_key),
):
    return await get_currency_history(
        db=db,
        base=base_currency,
        quote=quote_currency,
        range_=range,
    )
