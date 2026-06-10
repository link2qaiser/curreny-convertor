from enum import Enum
from pydantic import BaseModel, Field

from app.currency.models import CurrencyRate

_RESERVED_COLUMNS = {"id", "created_at"}
_CURRENCY_CODES = sorted(
    c.name for c in CurrencyRate.__table__.columns if c.name not in _RESERVED_COLUMNS
)

# Dynamically built so Swagger renders a dropdown of every supported code.
CurrencyCode = Enum("CurrencyCode", {code: code for code in _CURRENCY_CODES}, type=str)


class HistoryRange(str, Enum):
    D1 = "1D"
    W1 = "1W"
    M1 = "1M"
    M3 = "3M"
    M6 = "6M"
    Y1 = "1Y"
    Y5 = "5Y"


class HistoryPoint(BaseModel):
    t: int = Field(..., description="Unix timestamp (seconds, UTC) at the start of the bucket")
    v: float = Field(..., description="Exchange rate: 1 base = v quote")


class CurrencyHistoryResponse(BaseModel):
    base: str = Field(..., description="Base currency code (e.g. EUR)")
    quote: str = Field(..., description="Quote currency code (e.g. AED)")
    range: HistoryRange = Field(..., description="Range window of the series")
    granularity: str = Field(..., description="Bucket size used: hour | day | week | month")
    current: float | None = Field(None, description="Most recent rate in the window")
    change: float | None = Field(None, description="Absolute change from first to last point")
    change_pct: float | None = Field(None, description="Percent change from first to last point")
    high: float | None = Field(None, description="Maximum rate in the window")
    low: float | None = Field(None, description="Minimum rate in the window")
    points: list[HistoryPoint] = Field(default_factory=list, description="Time-ordered data points")


class HistoryErrorDetail(BaseModel):
    detail: str = Field(..., description="Human-readable error message")
