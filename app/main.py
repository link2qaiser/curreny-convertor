import logging.config
import asyncio
from datetime import datetime, timedelta, timezone
from app.currency.service import upload_to_s3, update_currency_rates
from app.currency.models import CurrencyRate
from app.utils.database import async_session
from fastapi import FastAPI
from app.utils.logging_config import LOGGING_CONFIG
from app.currency.routes import router as currency_router
from app.core.config import env_var
from app.services.slack_service import send_slack_alert
from sqlalchemy import select
# Load the logging config
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Currency Converter API",
    description="Provides pre-signed download URLs for the latest fiat and cryptocurrency exchange rates (150+ fiat currencies and top 50 cryptos, base USD). Rates are refreshed periodically from OpenExchangeRates and CoinMarketCap.",
    version="1.0.0",
)

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
            await asyncio.sleep(env_var.FETCH_API_DATA)  # Wait 1 hour
    
    async def periodic_rate_staleness_check():
        """Third background task - alert on Slack if rates are stale for 12h"""
        await asyncio.sleep(60)  # Initial delay
        while True:
            try:
                async with async_session() as db:
                    result = await db.execute(
                        select(CurrencyRate.created_at)
                        .order_by(CurrencyRate.created_at.desc())
                        .limit(1)
                    )
                    row = result.scalar_one_or_none()

                if row is None:
                    logger.warning("No currency rate row found in DB")
                    await send_slack_alert(
                        ":warning: *Currency Converter Alert*\n"
                        "No currency rate records found in the database."
                    )
                else:
                    last_updated = row if row.tzinfo else row.replace(tzinfo=timezone.utc)
                    age = datetime.now(timezone.utc) - last_updated
                    if age > timedelta(hours=12):
                        hours_ago = int(age.total_seconds() // 3600)
                        await send_slack_alert(
                            f":rotating_light: *Currency Converter Alert*\n"
                            f"Currency rates have *not been updated for {hours_ago} hours*.\n"
                            f"Last update: `{last_updated.strftime('%Y-%m-%d %H:%M UTC')}`"
                        )
                        logger.warning(f"Stale rate alert sent — last update {hours_ago}h ago")
                    else:
                        logger.info(f"Rate freshness OK — last update {int(age.total_seconds() // 60)}m ago")
            except Exception as e:
                logger.error(f"Rate staleness check failed: {e}")
            await asyncio.sleep(3600)  # Check every hour

    # Create both background tasks
    asyncio.create_task(periodic_s3_upload())
    asyncio.create_task(periodic_currency_update())
    asyncio.create_task(periodic_rate_staleness_check())

    logger.info("🚀 Background tasks started successfully")