from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.security import verify_api_key
from app.utils.database import async_session
from .service import get_currency_history
from .schema import (
    CurrencyHistoryResponse,
    CurrencyCode,
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
        "Returns a time-ordered series of `base → quote` exchange rates over the "
        "requested range, plus summary stats (current / change / high / low). "
        "Granularity is chosen automatically per range: hourly for 1D/1W, daily "
        "for 1M/3M/6M/1Y, weekly for 5Y."
    ),
    responses={
        200: {"model": CurrencyHistoryResponse},
        400: {"model": HistoryErrorDetail, "description": "Unknown base or quote currency code"},
        401: {"model": HistoryErrorDetail, "description": "Invalid API key"},
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
