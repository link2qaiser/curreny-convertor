from pydantic import BaseModel, Field


class GeoPingRequest(BaseModel):
    target: str = Field(..., description="Domain or IP address to ping")


class CurrencyURLResponse(BaseModel):
    url: str = Field(..., description="Pre-signed S3 URL to download the latest currency rates JSON")
    expires_at: int = Field(..., description="Unix timestamp (UTC) when the URL expires — 24 hours from generation")


class ErrorDetail(BaseModel):
    detail: str = Field(..., description="Human-readable error message")
