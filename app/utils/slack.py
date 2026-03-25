import aiohttp
import logging
from app.core.config import env_var

logger = logging.getLogger(__name__)


async def send_slack_alert(error_message: str, module: str, function_name: str) -> None:
    if not env_var.SLACK_WEBHOOK_URL:
        return

    env_label = env_var.ENV_STATE.upper()
    text = (
        f"*Exception Alert [{env_label}]*\n\n"
        f"*Error Message:* {error_message}\n\n"
        f"*Module:* `{module}`\n"
        f"*Function:* `{function_name}`"
    )

    try:
        async with aiohttp.ClientSession() as session:
            await session.post(env_var.SLACK_WEBHOOK_URL, json={"text": text})
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
