"""Configuration management for Sauti ya Mwananchi."""

import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google Cloud
    google_cloud_project: str = Field(default="fast-asset-496506-b8")
    google_cloud_location: str = Field(default="us-central1")
    google_genai_use_vertexai: bool = Field(default=True)
    google_api_key: str = Field(default="")
    
    # Africa's Talking
    at_username: str = Field(default="sandbox")
    at_api_key: str = Field(default="")
    at_environment: str = Field(default="sandbox")
    
    # Meta WhatsApp Cloud API
    meta_whatsapp_token: str = Field(default="")
    meta_whatsapp_phone_id: str = Field(default="")
    meta_webhook_verify_token: str = Field(default="sauti-verify-2026")
    
    # Vertex AI Search
    civic_datastore_id: str = Field(default="")
    
    # Security
    phone_hash_salt: str = Field(default="sauti-salt-2026")
    
    # App
    log_level: str = Field(default="INFO")
    port: int = Field(default=8080)

    @field_validator("meta_whatsapp_token", "meta_whatsapp_phone_id", "google_api_key", mode="after")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Singleton settings instance
_settings = None

def get_settings() -> Settings:
    """Dependency for retrieving settings (cached singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
