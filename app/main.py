import logging.config
import asyncio
from app.currency.service import upload_to_s3
from fastapi import FastAPI
from app.utils.logging_config import LOGGING_CONFIG
from app.currency.routes import router as currency_router

# Load the logging config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(currency_router)


from app.currency.service import upload_to_s3


@app.on_event("startup")
async def start_s3_background_task():
    async def periodic_upload():
        await asyncio.sleep(5)
        while True:
            try:
                await upload_to_s3()
                logger.info("✅ Background S3 upload completed")
            except Exception as e:
                logger.error(f"❌ S3 upload failed: {e}")
            await asyncio.sleep(60)  # every 10 minutes

    asyncio.create_task(periodic_upload())
