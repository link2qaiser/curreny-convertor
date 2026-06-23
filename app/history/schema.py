from datetime import date
from enum import Enum
from pydantic import BaseModel, Field


class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    FLAT = "flat"


class HistoryPoint(BaseModel):
    timestamp: int = Field(..., description="Unix timestamp in seconds (UTC)")
    date: str = Field(..., description="Human-readable date in ISO 8601 (UTC)")
    rate: float = Field(..., description="Exchange rate: 1 base_currency = rate quote_currency")


class CurrencyHistoryResponse(BaseModel):
    base_currency: str = Field(..., description="The currency you are converting FROM, e.g. AED")
    quote_currency: str = Field(..., description="The currency you are converting TO, e.g. PKR")

    start_date: date = Field(..., description="Window start (inclusive), YYYY-MM-DD UTC")
    end_date: date = Field(..., description="Window end (inclusive), YYYY-MM-DD UTC")
    interval: str = Field(..., description="Spacing between data points: hour, day, week, or month (auto-picked from the span)")

    starting_rate: float | None = Field(None, description="Rate at the beginning of the range")
    current_rate: float | None = Field(None, description="Most recent rate in the range")
    highest_rate: float | None = Field(None, description="Highest rate in the range")
    lowest_rate: float | None = Field(None, description="Lowest rate in the range")

    absolute_change: float | None = Field(
        None, description="current_rate minus starting_rate (in quote_currency units)"
    )
    percent_change: float | None = Field(
        None, description="absolute_change as a percentage of starting_rate"
    )
    direction: TrendDirection | None = Field(
        None, description="Overall trend across the range"
    )

    data_points: list[HistoryPoint] = Field(
        default_factory=list, description="Time-ordered data points to plot on the chart"
    )


class HistoryErrorDetail(BaseModel):
    detail: str = Field(..., description="Human-readable error message")
