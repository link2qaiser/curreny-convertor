import logging
import math
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

# Auto-tuned precision: target a fixed number of significant figures so the
# response stays readable for both large rates (USD/IDR ~16,000) and very
# small ones (BTC pairs ~0.00001), and so tiny % changes never round to 0.
RATE_SIG_FIGURES = 6
PERCENT_SIG_FIGURES = 3
DECIMALS_MIN = 2
DECIMALS_MAX = 10


def _auto_decimals(value: float, sig_figures: int) -> int:
    """Decimal places needed to display `value` at `sig_figures` significant digits."""
    if value is None or value == 0 or not math.isfinite(value):
        return DECIMALS_MIN
    magnitude = math.floor(math.log10(abs(value)))
    return max(DECIMALS_MIN, min(DECIMALS_MAX, sig_figures - magnitude - 1))

# Whitelist of valid currency column names — prevents SQL injection via user input.
_RESERVED_COLUMNS = {"id", "created_at"}
SUPPORTED_CURRENCY_CODES: frozenset[str] = frozenset(
    c.name for c in CurrencyRate.__table__.columns if c.name not in _RESERVED_COLUMNS
)

# (window_delta, bucket_unit) per range.
# bucket_unit None = raw hourly rows; window None = "all available data".
_RANGE_CONFIG: dict[HistoryRange, tuple[timedelta | None, str | None]] = {
    HistoryRange.ONE_DAY:      (timedelta(days=1),      None),
    HistoryRange.ONE_WEEK:     (timedelta(days=7),      None),
    HistoryRange.ONE_MONTH:    (timedelta(days=30),     "day"),
    HistoryRange.THREE_MONTHS: (timedelta(days=90),     "day"),
    HistoryRange.SIX_MONTHS:   (timedelta(days=180),    "day"),
    HistoryRange.ONE_YEAR:     (timedelta(days=365),    "day"),
    HistoryRange.THREE_YEARS:  (timedelta(days=365*3),  "week"),
    HistoryRange.FIVE_YEARS:   (timedelta(days=365*5),  "week"),
    HistoryRange.TEN_YEARS:    (timedelta(days=365*10), "month"),
    HistoryRange.ALL:          (None,                   None),  # auto-picked below
}


def _auto_bucket_for_span(span: timedelta) -> str | None:
    """Pick a bucket size so the chart has a sensible number of points."""
    if span <= timedelta(days=7):
        return None  # raw hourly
    if span <= timedelta(days=90):
        return "day"
    if span <= timedelta(days=365 * 3):
        return "week"
    return "month"


def _build_point(ts: datetime, base_value: float, quote_value: float) -> HistoryPoint:
    # Don't round here — final precision is applied uniformly after the pair-wide
    # decimal count is known from the most recent rate.
    return HistoryPoint(
        timestamp=int(ts.timestamp()),
        date=ts.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        rate=quote_value / base_value,
    )


def _classify_direction(absolute_change: float, rate_decimals: int) -> TrendDirection:
    # "Flat" if the change is smaller than the displayable precision.
    threshold = 10 ** (-rate_decimals)
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
    now = datetime.now(timezone.utc)
    today_iso = now.isoformat().replace("+00:00", "Z")

    base_col = getattr(CurrencyRate, base)
    quote_col = getattr(CurrencyRate, quote)

    # For ALL: window starts at the earliest available row; bucket auto-picked from span.
    if window is None:
        earliest_row = (await db.execute(
            select(func.min(CurrencyRate.created_at))
            .where(base_col.isnot(None))
            .where(quote_col.isnot(None))
            .where(base_col > 0)
        )).scalar_one_or_none()
        if earliest_row is None:
            return CurrencyHistoryResponse(
                base_currency=base, quote_currency=quote, range=range_,
                interval="hour", today_date=today_iso, data_points=[],
            )
        earliest = earliest_row if earliest_row.tzinfo else earliest_row.replace(tzinfo=timezone.utc)
        since = earliest
        bucket_unit = _auto_bucket_for_span(now - earliest)
    else:
        since = now - window

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

    start_iso = since.isoformat().replace("+00:00", "Z")

    if not data_points:
        return CurrencyHistoryResponse(
            base_currency=base,
            quote_currency=quote,
            range=range_,
            interval=interval,
            start_date=start_iso,
            today_date=today_iso,
            data_points=[],
        )

    rates = [point.rate for point in data_points]
    raw_current = rates[-1]
    raw_starting = rates[0]

    # Pair-wide decimals derived from the most recent rate keep all points and
    # stats at a consistent scale (no ragged chart).
    rate_decimals = _auto_decimals(raw_current, RATE_SIG_FIGURES)
    for point in data_points:
        point.rate = round(point.rate, rate_decimals)

    starting_rate = round(raw_starting, rate_decimals)
    current_rate = round(raw_current, rate_decimals)
    highest_rate = round(max(rates), rate_decimals)
    lowest_rate = round(min(rates), rate_decimals)

    raw_change = raw_current - raw_starting
    absolute_change = round(raw_change, rate_decimals)

    if raw_starting:
        raw_pct = (raw_change / raw_starting) * 100.0
        percent_decimals = _auto_decimals(raw_pct, PERCENT_SIG_FIGURES)
        percent_change = round(raw_pct, percent_decimals)
    else:
        percent_change = None

    direction = _classify_direction(raw_change, rate_decimals)

    return CurrencyHistoryResponse(
        base_currency=base,
        quote_currency=quote,
        range=range_,
        interval=interval,
        start_date=start_iso,
        today_date=today_iso,
        starting_rate=starting_rate,
        current_rate=current_rate,
        highest_rate=highest_rate,
        lowest_rate=lowest_rate,
        absolute_change=absolute_change,
        percent_change=percent_change,
        direction=direction,
        data_points=data_points,
    )
