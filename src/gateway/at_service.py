"""Africa's Talking SDK integration for outbound SMS replies."""

import africastalking
from src.config import get_settings
import logging

logger = logging.getLogger(__name__)

_initialized = False


def _ensure_initialized():
    """Initialize the AT SDK once."""
    global _initialized
    if not _initialized:
        settings = get_settings()
        if settings.at_api_key:
            africastalking.initialize(
                username=settings.at_username,
                api_key=settings.at_api_key
            )
            _initialized = True
        else:
            logger.warning("AT API key not set — SMS sending disabled.")


def send_sms(to_phone: str, message: str):
    """Send an outbound SMS reply via Africa's Talking."""
    _ensure_initialized()
    if not _initialized:
        return None

    sms = africastalking.SMS
    try:
        response = sms.send(message, [to_phone])
        logger.info(f"SMS sent to {to_phone[:6]}...: {response}")
        return response
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        return None
