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
)

logger = logging.getLogger(__name__)

# Whitelist of valid currency column names — prevents SQL injection via user input.
_RESERVED_COLUMNS = {"id", "created_at"}
SUPPORTED_CURRENCY_CODES: frozenset[str] = frozenset(
    c.name for c in CurrencyRate.__table__.columns if c.name not in _RESERVED_COLUMNS
)

# (window_delta, bucket_unit) per range. bucket_unit None = raw hourly rows.
_RANGE_CONFIG: dict[HistoryRange, tuple[timedelta, str | None]] = {
    HistoryRange.D1: (timedelta(days=1),     None),
    HistoryRange.W1: (timedelta(days=7),     None),
    HistoryRange.M1: (timedelta(days=30),    "day"),
    HistoryRange.M3: (timedelta(days=90),    "day"),
    HistoryRange.M6: (timedelta(days=180),   "day"),
    HistoryRange.Y1: (timedelta(days=365),   "day"),
    HistoryRange.Y5: (timedelta(days=365*5), "week"),
}


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
        points = [
            HistoryPoint(t=int(ts.timestamp()), v=q / b)
            for ts, b, q in rows
        ]
        granularity = "hour"
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
        points = [
            HistoryPoint(t=int(ts.timestamp()), v=float(q) / float(b))
            for ts, b, q in rows if b and float(b) > 0
        ]
        granularity = bucket_unit

    if not points:
        return CurrencyHistoryResponse(
            base=base, quote=quote, range=range_, granularity=granularity, points=[],
        )

    values = [p.v for p in points]
    first, last = values[0], values[-1]
    change = last - first
    change_pct = (change / first * 100.0) if first else None

    return CurrencyHistoryResponse(
        base=base,
        quote=quote,
        range=range_,
        granularity=granularity,
        current=last,
        change=change,
        change_pct=change_pct,
        high=max(values),
        low=min(values),
        points=points,
    )
