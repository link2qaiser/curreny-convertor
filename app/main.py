import logging.config
import asyncio
from app.currency.service import upload_to_s3, update_currency_rates
from app.utils.database import async_session
from fastapi import FastAPI
from app.utils.logging_config import LOGGING_CONFIG
from app.currency.routes import router as currency_router
from app.core.config import env_var
# Load the logging config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(currency_router)

@app.on_event("startup")
async def start_background_tasks():
    
    async def periodic_s3_upload():
        """First background task - S3 upload every minute"""
        await asyncio.sleep(5)  # Initial delay
        while True:
            try:
                await upload_to_s3()
                logger.info("✅ Background S3 upload completed")
            except Exception as e:
                logger.error(f"❌ S3 upload failed: {e}")
            await asyncio.sleep(env_var.WRITE_FILE_ON_S3)
    
    # async def periodic_currency_update():
    #     """Second background task - Update currency rates every minute"""
    #     await asyncio.sleep(10)  # Initial delay (different from first task)
    #     while True:
    #         try:
    #             # Create database session
    #             async with async_session() as db:
    #                 await update_currency_rates(db)
    #             logger.info("✅ Currency rates update completed")
    #         except Exception as e:
    #             logger.error(f"❌ Currency rates update failed: {e}")
    #         await asyncio.sleep(env_var.FETCH_API_DATA)  # Wait 1 minute
    
    # Create both background tasks
    asyncio.create_task(periodic_s3_upload())
    #asyncio.create_task(periodic_currency_update())
    
    logger.info("🚀 Background tasks started successfully")