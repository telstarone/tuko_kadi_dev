"""Main Entry Point for Sauti ya Mwananchi FastAPI Gateway."""

from fastapi import FastAPI
from src.gateway.webhooks import router as webhook_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sauti ya Mwananchi Gateway",
    description="Multi-channel civic participation gateway (SMS, USSD, WhatsApp)",
    version="2.0.0"
)

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sauti-ya-mwananchi", "version": "2.0.0"}

@app.get("/")
async def root():
    return {
        "service": "Sauti ya Mwananchi",
        "version": "2.0.0",
        "channels": {
            "sms": "/webhook/sms",
            "ussd": "/webhook/ussd",
            "whatsapp": "/webhook/whatsapp (Meta Cloud API)"
        },
        "health": "/health"
    }

# Include routers
app.include_router(webhook_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
