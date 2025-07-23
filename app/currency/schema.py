from pydantic import BaseModel, Field

class GeoPingRequest(BaseModel):
    target: str = Field(..., description="Domain or IP address to ping")
