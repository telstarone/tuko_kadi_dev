"""Tests for Gateway Webhooks (AT + Meta WhatsApp)."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_shows_channels():
    response = client.get("/")
    assert response.status_code == 200
    assert "whatsapp" in response.json()["channels"]


def test_sms_webhook():
    payload = {
        "from": "+254712345678",
        "to": "12345",
        "text": "Hello Sauti",
        "id": "sms-123"
    }
    response = client.post("/webhook/sms", data=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ussd_initial_dial():
    payload = {
        "sessionId": "ussd-123",
        "phoneNumber": "+254712345678",
        "serviceCode": "*384*9196#",
        "text": ""
    }
    response = client.post("/webhook/ussd", data=payload)
    assert response.status_code == 200
    assert response.text.startswith("CON")
    assert "Welcome" in response.text


def test_ussd_selection():
    payload = {
        "sessionId": "ussd-456",
        "phoneNumber": "+254712345678",
        "serviceCode": "*384*9196#",
        "text": "1"
    }
    response = client.post("/webhook/ussd", data=payload)
    assert response.status_code == 200
    assert response.text.startswith("END")


def test_whatsapp_verification_success():
    response = client.get(
        "/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "test-challenge-123",
            "hub.verify_token": "sauti-verify-2026"
        }
    )
    assert response.status_code == 200
    assert response.text == "test-challenge-123"


def test_whatsapp_verification_failure():
    response = client.get(
        "/webhook/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "test-challenge-123",
            "hub.verify_token": "wrong-token"
        }
    )
    assert response.status_code == 403


def test_whatsapp_message():
    meta_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "messages": [{
                        "from": "254712345678",
                        "id": "msg-1",
                        "type": "text",
                        "text": {"body": "What are my voting rights?"}
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    response = client.post("/webhook/whatsapp", json=meta_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_whatsapp_status_update():
    """Status updates should be acknowledged silently."""
    status_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "statuses": [{"id": "msg-1", "status": "delivered"}]
                },
                "field": "messages"
            }]
        }]
    }
    response = client.post("/webhook/whatsapp", json=status_payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
