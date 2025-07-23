from app.utils.database import async_session
from .models import CurrencyRate
from app.services.s3_service import S3Service
from app.core.config import env_var
from sqlalchemy import select
from datetime import datetime


async def upload_to_s3():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(CurrencyRate).order_by(CurrencyRate.created_at.desc()).limit(1)
            )
            latest = result.scalar_one_or_none()

            if not latest:
                raise Exception("No currency rate found.")

            data = {}
            for col in CurrencyRate.__table__.columns:
                value = getattr(latest, col.name)
                if value is not None:
                    # Convert datetime to ISO string for JSON serialization
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    data[col.name] = value

            service = S3Service()
            url = service.upload_json_data(
                data=data, filename="latest.json", folder="currency"
            )
            return {"success": True, "url": url}


async def get_from_s3():
    key = f"{env_var.ENV_STATE}/currency/latest.json"

    service = S3Service()

    try:
        signed_url = service.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": env_var.DO_SPACES_BUCKET, "Key": key},
            ExpiresIn=300 
        )
        return {"url": signed_url}
    except Exception as e:
        return {"error": str(e)}