import aiohttp
import logging
from app.core.config import env_var

logger = logging.getLogger(__name__)

SLACK_CHANNEL = "#cc-alerts"


async def send_slack_alert(message: str) -> bool:
    webhook_url = env_var.SLACK_WEBHOOK_URL
    if not webhook_url:
        logger.warning("SLACK_WEBHOOK_URL not configured — skipping Slack alert")
        return False

    payload = {
        "channel": SLACK_CHANNEL,
        "text": message,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Slack alert sent to {SLACK_CHANNEL}")
                    return True
                else:
                    text = await response.text()
                    logger.error(f"Slack alert failed: {response.status} — {text}")
                    return False
    except Exception:
        logger.exception("Error sending Slack alert")
        return False
