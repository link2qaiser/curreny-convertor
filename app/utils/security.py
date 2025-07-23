from app.core.config import env_var
from fastapi import HTTPException, Header

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != env_var.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")