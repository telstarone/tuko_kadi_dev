"""Webhook Handlers — AT (SMS/USSD) and Meta WhatsApp Cloud API."""

import logging
from fastapi import APIRouter, Request, Response, Query
from src.gateway.normalizer import normalize_sms, normalize_ussd, normalize_meta_whatsapp
from src.gateway.formatter import format_response
from src.agents.runner import process_message
from src.gateway.at_service import send_sms
from src.gateway.meta_whatsapp import send_whatsapp_message
from src.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhooks"])


# ── Africa's Talking: SMS ────────────────────────────────────────────

@router.post("/sms")
async def sms_webhook(request: Request):
    """Handle inbound SMS from Africa's Talking."""
    try:
        form_data = dict(await request.form())
        envelope = normalize_sms(form_data)
        response_text = await process_message(envelope)
        formatted = format_response(response_text, "sms")
        send_sms(form_data.get("from", ""), formatted)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"SMS webhook error: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}


# ── Africa's Talking: USSD ───────────────────────────────────────────

@router.post("/ussd")
async def ussd_webhook(request: Request):
    """Handle inbound USSD from Africa's Talking."""
    try:
        form_data = dict(await request.form())
        envelope = normalize_ussd(form_data)

        if not envelope.text:
            menu = "Welcome to Sauti ya Mwananchi\n1. Rights\n2. Station\n3. Fact Check"
            return Response(
                content=format_response(menu, "ussd", end_session=False),
                media_type="text/plain"
            )

        response_text = await process_message(envelope)
        return Response(
            content=format_response(response_text, "ussd"),
            media_type="text/plain"
        )
    except Exception as e:
        logger.error(f"USSD webhook error: {e}", exc_info=True)
        return Response(content="END An error occurred.", media_type="text/plain")


# ── Meta WhatsApp Cloud API ──────────────────────────────────────────

@router.get("/whatsapp")
async def whatsapp_verify(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """Meta webhook verification (GET challenge-response)."""
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_webhook_verify_token:
        logger.info("Meta WhatsApp webhook verified successfully.")
        return Response(content=hub_challenge, media_type="text/plain")
    logger.warning(f"WhatsApp verification failed: mode={hub_mode}")
    return Response(content="Forbidden", status_code=403)


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle inbound WhatsApp messages from Meta Cloud API."""
    try:
        payload = await request.json()
        envelope = normalize_meta_whatsapp(payload)

        if envelope is None:
            # Status update or non-message event — acknowledge silently
            return {"status": "ok"}

        response_text = await process_message(envelope)
        formatted = format_response(response_text, "whatsapp")

        # Extract original sender phone from Meta payload
        try:
            sender = payload["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
            await send_whatsapp_message(sender, formatted)
        except (KeyError, IndexError):
            logger.warning("Could not extract sender for WhatsApp reply.")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}
