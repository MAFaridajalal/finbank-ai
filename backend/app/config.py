"""
Configuration management for FinBank AI backend.
Loads settings from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "FinBank AI"
    debug: bool = False

    # Database
    database_url: str = "mssql+pyodbc://localhost/finbank?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"

    # LLM Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_key: Optional[str] = None
    azure_openai_deployment: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"

    # Default LLM provider
    default_llm_provider: str = "openai"  # openai, claude, azure, ollama

    # Azure AD
    azure_ad_tenant_id: Optional[str] = None
    azure_ad_client_id: Optional[str] = None
    azure_ad_client_secret: Optional[str] = None

    # CORS
    cors_origins: list[str] = ["http://localhost:4200", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
