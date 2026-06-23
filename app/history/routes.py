from datetime import date, timedelta, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.security import verify_api_key
from app.utils.database import async_session
from .service import get_currency_history
from .schema import CurrencyHistoryResponse, HistoryErrorDetail

router = APIRouter(prefix="/history", tags=["history"])


async def _db():
    async with async_session() as session:
        yield session


def _default_end_date() -> date:
    return datetime.now(timezone.utc).date()


def _default_start_date() -> date:
    return _default_end_date() - timedelta(days=30)


@router.get(
    "",
    response_model=CurrencyHistoryResponse,
    status_code=200,
    summary="Get historical exchange-rate series for a currency pair",
    description=(
        "Returns the `base_currency -> quote_currency` exchange-rate series "
        "between `start_date` and `end_date` (inclusive), plus summary stats "
        "(starting_rate, current_rate, highest_rate, lowest_rate, "
        "absolute_change, percent_change, direction).\n\n"
        "Spacing between data points is auto-picked from the span: hourly "
        "for ≤7 days, daily for ≤90 days, weekly for ≤3 years, monthly otherwise. "
        "Defaults: last 30 days."
    ),
    responses={
        200: {"model": CurrencyHistoryResponse},
        400: {"model": HistoryErrorDetail, "description": "Bad currency code or invalid date range"},
        401: {"model": HistoryErrorDetail, "description": "Invalid API key"},
        422: {"description": "Missing or malformed query params"},
    },
)
async def get_currency_history_endpoint(
    base_currency: str = Query(
        ..., min_length=3, max_length=5, example="EUR",
        description="Currency you are converting FROM (e.g. EUR, USD, BTC).",
    ),
    quote_currency: str = Query(
        ..., min_length=3, max_length=5, example="AED",
        description="Currency you are converting TO (e.g. AED, PKR, INR).",
    ),
    start_date: date = Query(
        default_factory=_default_start_date,
        description="Window start (inclusive), YYYY-MM-DD UTC. Defaults to 30 days ago.",
    ),
    end_date: date = Query(
        default_factory=_default_end_date,
        description="Window end (inclusive), YYYY-MM-DD UTC. Defaults to today.",
    ),
    db: AsyncSession = Depends(_db),
    _: str = Depends(verify_api_key),
):
    return await get_currency_history(
        db=db,
        base=base_currency,
        quote=quote_currency,
        start_date=start_date,
        end_date=end_date,
    )
