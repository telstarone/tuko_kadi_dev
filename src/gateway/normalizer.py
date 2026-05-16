"""Normalize inbound payloads into standard MessageEnvelopes."""

from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
import hashlib
from src.config import get_settings

class MessageEnvelope(BaseModel):
    """Standardized message format for the agent pipeline."""
    phone_hash: str
    session_id: str
    text: Optional[str] = ""
    channel: str  # "sms", "ussd", "whatsapp"
    media_url: Optional[str] = None
    raw_payload: dict


def _hash_phone(phone: str) -> str:
    """Hash phone number for zero-retention privacy."""
    salt = get_settings().phone_hash_salt
    return hashlib.sha256(f"{phone}{salt}".encode()).hexdigest()[:16]


# --- Africa's Talking Normalizers ---

def normalize_sms(payload: dict) -> MessageEnvelope:
    """Normalize AT SMS callback payload."""
    return MessageEnvelope(
        phone_hash=_hash_phone(payload.get("from", "unknown")),
        session_id=payload.get("id", "none"),
        text=payload.get("text", ""),
        channel="sms",
        raw_payload=payload
    )

def normalize_ussd(payload: dict) -> MessageEnvelope:
    """Normalize AT USSD callback payload."""
    return MessageEnvelope(
        phone_hash=_hash_phone(payload.get("phoneNumber", "unknown")),
        session_id=payload.get("sessionId", "none"),
        text=payload.get("text", ""),
        channel="ussd",
        raw_payload=payload
    )

def normalize_at_whatsapp(payload: dict) -> MessageEnvelope:
    """Normalize AT WhatsApp callback payload."""
    return MessageEnvelope(
        phone_hash=_hash_phone(payload.get("from", "unknown")),
        session_id=payload.get("id", f"wa-{payload.get('from')}"),
        text=payload.get("text", ""),
        channel="whatsapp",
        media_url=payload.get("mediaUrl"),
        raw_payload=payload
    )


# --- Meta WhatsApp Cloud API Normalizer ---

def normalize_meta_whatsapp(payload: dict) -> Optional[MessageEnvelope]:
    """Normalize Meta WhatsApp Cloud API webhook payload.

    Meta sends a nested structure. Returns None if the payload
    does not contain a user message (e.g. status updates).
    """
    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return None  # Status update, not a user message

        msg = messages[0]
        sender = msg.get("from", "unknown")
        msg_type = msg.get("type", "text")

        text = ""
        media_url = None

        if msg_type == "text":
            text = msg.get("text", {}).get("body", "")
        elif msg_type == "image":
            media_url = msg.get("image", {}).get("id", "")
            text = msg.get("image", {}).get("caption", "I sent an image")
        elif msg_type == "interactive":
            interactive = msg.get("interactive", {})
            if interactive.get("type") == "button_reply":
                text = interactive.get("button_reply", {}).get("title", "")
            elif interactive.get("type") == "list_reply":
                text = interactive.get("list_reply", {}).get("title", "")

        return MessageEnvelope(
            phone_hash=_hash_phone(sender),
            session_id=f"meta-wa-{_hash_phone(sender)}",
            text=text,
            channel="whatsapp",
            media_url=media_url,
            raw_payload=payload
        )
    except (IndexError, KeyError):
        return None
