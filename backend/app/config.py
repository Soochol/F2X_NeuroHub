"""
Application Configuration using Pydantic Settings.

Environment variables can be set in .env file:
    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY=your-secret-key-here
    DEBUG=True
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "F2X NeuroHub MES API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./dev.db"  # Force SQLite for local development
    DB_ECHO: bool = False  # SQLAlchemy echo SQL statements

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Printer
    PRINTER_QUEUE_NAME: str = "ZDesigner GK420t"  # Default Zebra printer name

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
