from app.utils.database import async_session
from .models import CurrencyRate
from app.services.s3_service import S3Service
from app.core.config import env_var
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import aiohttp
import logging
from datetime import datetime, timedelta, timezone
# Setup logger
logger = logging.getLogger(__name__)

# API Keys
OPENEXCHANGE_API_KEY = env_var.OPENEXCHANGERATES_API_KEY or ""
COINMARKETCAP_API_KEY = env_var.COINMARKETCAP_API_KEY or ""

# URLs
OPENEXCHANGE_URL = (
    f"https://openexchangerates.org/api/latest.json?app_id={OPENEXCHANGE_API_KEY}"
)
COINMARKETCAP_URL = (
    "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    "?limit=50&convert=USD"
)

SUPPORTED_CRYPTO_SYMBOLS = {
    "BTC", "ETH", "USDT", "BNB", "SOL", "USDC", "XRP", "TON", "DOGE", "ADA",
    "AVAX", "TRX", "LINK", "DOT", "WBTC", "SHIB", "BCH", "LTC", "ICP", "MATIC",
    "UNI", "ETC", "XLM", "APT", "NEAR", "OKB", "LDO", "FIL", "MNT", "HBAR",
    "CRO", "STX", "INJ", "RNDR", "IMX", "ARB", "VET", "MKR", "AAVE", "KAS",
    "QNT", "GRT", "ALGO", "OP", "SAND", "EGLD", "XTZ", "RUNE", "FTM", "EOS"
}


async def upload_to_s3():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(CurrencyRate).order_by(CurrencyRate.created_at.desc()).limit(1)
            )
            latest = result.scalar_one_or_none()

            if not latest:
                logger.warning("No currency rate found to upload.")
                return {"success": False, "message": "No currency rate found"}

            data = {}
            for col in CurrencyRate.__table__.columns:
                value = getattr(latest, col.name)
                if value is not None:
                    data[col.name] = value.isoformat() if isinstance(value, datetime) else value

            try:
                service = S3Service()
                url = service.upload_json_data(data=data, filename="latest.json", folder="currency")
                logger.info(f"Uploaded currency rates to S3: {url}")
                return {"success": True, "url": url}
            except Exception as e:
                logger.exception("Failed to upload currency rates to S3")
                return {"success": False, "message": str(e)}


async def get_from_s3():
    key = f"{env_var.ENV_STATE}/currency/latest.json"
    service = S3Service()
    expires_in = 86400  # 1 day

    try:
        signed_url = service.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": env_var.DO_SPACES_BUCKET, "Key": key},
            ExpiresIn=expires_in
        )
        expiry_time = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        expiry_unix_timestamp = int(expiry_time.timestamp())

        logger.info(f"Generated signed S3 URL: {signed_url}")
        return {
            "url": signed_url,
            "expires_at": expiry_unix_timestamp
        }
    except Exception as e:
        logger.exception("Failed to generate signed S3 URL")
        return {"error": str(e)}

async def fetch_openexchange_rates() -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(OPENEXCHANGE_URL) as response:
                if response.status != 200:
                    logger.error(f"Failed OpenExchangeRates fetch, status: {response.status}")
                    return {}
                return await response.json()
    except Exception as e:
        logger.exception("Error fetching OpenExchangeRates")
        return {}


async def fetch_coinmarketcap_rates() -> list[dict]:
    headers = {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(COINMARKETCAP_URL, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Failed CoinMarketCap fetch, status: {response.status}")
                    return []
                result = await response.json()
                return result.get("data", [])
    except Exception as e:
        logger.exception("Error fetching CoinMarketCap data")
        return []


async def update_currency_rates(db: AsyncSession) -> CurrencyRate | None:
    try:
        logger.info("🔄 Fetching exchange rates...")

        open_data = await fetch_openexchange_rates()
        cmc_data = await fetch_coinmarketcap_rates()

        rates = open_data.get("rates", {})
        db_rates = CurrencyRate(USD=1.0)

        for currency_code, rate in rates.items():
            if hasattr(db_rates, currency_code):
                setattr(db_rates, currency_code, rate)

        for coin in cmc_data:
            symbol = coin.get("symbol")
            usd_price = coin.get("quote", {}).get("USD", {}).get("price")

            if (
                symbol in SUPPORTED_CRYPTO_SYMBOLS
                and isinstance(usd_price, (int, float))
                and usd_price > 0
            ):
                if hasattr(db_rates, symbol):
                    setattr(db_rates, symbol, 1 / usd_price)
                else:
                    logger.warning(f"⚠️ Symbol '{symbol}' not found in model")

        db.add(db_rates)
        await db.commit()
        await db.refresh(db_rates)

        logger.info(f"✅ Currency + crypto rates updated at {datetime.now()}")
        return db_rates

    except Exception as e:
        logger.exception("❌ Error updating currency rates")
        await db.rollback()
        return None
