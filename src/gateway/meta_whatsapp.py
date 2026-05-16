"""Meta WhatsApp Cloud API — outbound message service."""

import httpx
from src.config import get_settings
import logging

logger = logging.getLogger(__name__)

META_API_URL = "https://graph.facebook.com/v21.0/{phone_id}/messages"


async def send_whatsapp_message(to_phone: str, message: str) -> dict | None:
    """Send a WhatsApp reply via Meta Cloud API.
    
    Args:
        to_phone: Recipient phone number (international format, no +).
        message: The text message to send.
    
    Returns:
        Meta API response dict, or None on failure.
    """
    settings = get_settings()
    
    if not settings.meta_whatsapp_token or not settings.meta_whatsapp_phone_id:
        logger.warning(f"Meta WhatsApp not configured. Token present: {bool(settings.meta_whatsapp_token)}, Phone ID: {settings.meta_whatsapp_phone_id}")
        return None
    
    url = META_API_URL.format(phone_id=settings.meta_whatsapp_phone_id)
    headers = {
        "Authorization": f"Bearer {settings.meta_whatsapp_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message}
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            logger.info(f"WhatsApp sent to {to_phone[:6]}...: {resp.status_code}")
            return resp.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"Meta WhatsApp API error: {e.response.status_code} — {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return None
