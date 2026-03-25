import logging.config
import asyncio
import traceback
from app.currency.service import upload_to_s3, update_currency_rates
from app.utils.database import async_session
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.utils.logging_config import LOGGING_CONFIG
from app.currency.routes import router as currency_router
from app.core.config import env_var
from app.utils.slack import send_slack_alert
# Load the logging config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Currency Converter API",
    description="Provides pre-signed download URLs for the latest fiat and cryptocurrency exchange rates (150+ fiat currencies and top 50 cryptos, base USD). Rates are refreshed periodically from OpenExchangeRates and CoinMarketCap.",
    version="1.0.0",
)

app.include_router(currency_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code >= 500:
        tb = traceback.extract_tb(exc.__traceback__)
        last = tb[-1] if tb else None
        module = ("app." + last.filename.split("/app/")[-1].replace("/", ".").removesuffix(".py")) if last else "unknown"
        await send_slack_alert(
            error_message=str(exc.detail),
            module=module,
            function_name=last.name if last else "unknown",
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    tb = traceback.extract_tb(exc.__traceback__)
    last = tb[-1] if tb else None
    module = ("app." + last.filename.split("/app/")[-1].replace("/", ".").removesuffix(".py")) if last else "unknown"
    logger.exception("Unhandled exception")
    await send_slack_alert(
        error_message=str(exc),
        module=module,
        function_name=last.name if last else "unknown",
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

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
                await send_slack_alert(
                    error_message=str(e),
                    module="app.currency.service",
                    function_name="upload_to_s3",
                )
            await asyncio.sleep(env_var.WRITE_FILE_ON_S3)
    
    async def periodic_currency_update():
        """Second background task - Update currency rates every hour"""
        await asyncio.sleep(10)  # Initial delay (different from first task)
        while True:
            try:
                async with async_session() as db:
                    await update_currency_rates(db)
                logger.info("✅ Currency rates update completed")
            except Exception as e:
                logger.error(f"❌ Currency rates update failed: {e}")
                await send_slack_alert(
                    error_message=str(e),
                    module="app.currency.service",
                    function_name="update_currency_rates",
                )
            await asyncio.sleep(env_var.FETCH_API_DATA)  # Wait 1 hour
    
    # Create both background tasks
    asyncio.create_task(periodic_s3_upload())
    asyncio.create_task(periodic_currency_update())
    
    logger.info("🚀 Background tasks started successfully")