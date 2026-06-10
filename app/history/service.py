import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.currency.models import CurrencyRate
from .schema import (
    HistoryRange,
    HistoryPoint,
    CurrencyHistoryResponse,
    TrendDirection,
)

logger = logging.getLogger(__name__)

# Precision for displayed numbers in the API response.
RATE_DECIMALS = 6
PERCENT_DECIMALS = 2

# Whitelist of valid currency column names — prevents SQL injection via user input.
_RESERVED_COLUMNS = {"id", "created_at"}
SUPPORTED_CURRENCY_CODES: frozenset[str] = frozenset(
    c.name for c in CurrencyRate.__table__.columns if c.name not in _RESERVED_COLUMNS
)

# (window_delta, bucket_unit) per range. bucket_unit None = raw hourly rows.
_RANGE_CONFIG: dict[HistoryRange, tuple[timedelta, str | None]] = {
    HistoryRange.ONE_DAY:      (timedelta(days=1),     None),
    HistoryRange.ONE_WEEK:     (timedelta(days=7),     None),
    HistoryRange.ONE_MONTH:    (timedelta(days=30),    "day"),
    HistoryRange.THREE_MONTHS: (timedelta(days=90),    "day"),
    HistoryRange.SIX_MONTHS:   (timedelta(days=180),   "day"),
    HistoryRange.ONE_YEAR:     (timedelta(days=365),   "day"),
    HistoryRange.FIVE_YEARS:   (timedelta(days=365*5), "week"),
}


def _build_point(ts: datetime, base_value: float, quote_value: float) -> HistoryPoint:
    rate = round(quote_value / base_value, RATE_DECIMALS)
    return HistoryPoint(
        timestamp=int(ts.timestamp()),
        date=ts.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        rate=rate,
    )


def _classify_direction(absolute_change: float) -> TrendDirection:
    # "Flat" if the change is smaller than the displayable precision.
    threshold = 10 ** (-RATE_DECIMALS)
    if absolute_change > threshold:
        return TrendDirection.UP
    if absolute_change < -threshold:
        return TrendDirection.DOWN
    return TrendDirection.FLAT


async def get_currency_history(
    db: AsyncSession, base: str, quote: str, range_: HistoryRange,
) -> CurrencyHistoryResponse:
    base = base.upper()
    quote = quote.upper()
    if base not in SUPPORTED_CURRENCY_CODES:
        raise HTTPException(status_code=400, detail=f"Unsupported base currency: {base}")
    if quote not in SUPPORTED_CURRENCY_CODES:
        raise HTTPException(status_code=400, detail=f"Unsupported quote currency: {quote}")

    window, bucket_unit = _RANGE_CONFIG[range_]
    since = datetime.now(timezone.utc) - window

    base_col = getattr(CurrencyRate, base)
    quote_col = getattr(CurrencyRate, quote)

    if bucket_unit is None:
        stmt = (
            select(CurrencyRate.created_at, base_col, quote_col)
            .where(CurrencyRate.created_at >= since)
            .where(base_col.isnot(None))
            .where(quote_col.isnot(None))
            .where(base_col > 0)
            .order_by(CurrencyRate.created_at.asc())
        )
        rows = (await db.execute(stmt)).all()
        data_points = [_build_point(ts, float(b), float(q)) for ts, b, q in rows]
        interval = "hour"
    else:
        bucket = func.date_trunc(bucket_unit, CurrencyRate.created_at)
        stmt = (
            select(bucket.label("bucket"), func.avg(base_col), func.avg(quote_col))
            .where(CurrencyRate.created_at >= since)
            .where(base_col.isnot(None))
            .where(quote_col.isnot(None))
            .where(base_col > 0)
            .group_by(bucket)
            .order_by(bucket.asc())
        )
        rows = (await db.execute(stmt)).all()
        data_points = [
            _build_point(ts, float(b), float(q))
            for ts, b, q in rows if b and float(b) > 0
        ]
        interval = bucket_unit

    if not data_points:
        return CurrencyHistoryResponse(
            base_currency=base,
            quote_currency=quote,
            range=range_,
            interval=interval,
            data_points=[],
        )

    rates = [point.rate for point in data_points]
    starting_rate = rates[0]
    current_rate = rates[-1]
    highest_rate = max(rates)
    lowest_rate = min(rates)

    absolute_change = round(current_rate - starting_rate, RATE_DECIMALS)
    percent_change = (
        round((absolute_change / starting_rate) * 100.0, PERCENT_DECIMALS)
        if starting_rate else None
    )
    direction = _classify_direction(absolute_change)

    return CurrencyHistoryResponse(
        base_currency=base,
        quote_currency=quote,
        range=range_,
        interval=interval,
        starting_rate=starting_rate,
        current_rate=current_rate,
        highest_rate=highest_rate,
        lowest_rate=lowest_rate,
        absolute_change=absolute_change,
        percent_change=percent_change,
        direction=direction,
        data_points=data_points,
    )
