"""
Application Configuration using Pydantic Settings.

Environment variables can be set in .env file:
    DATABASE_URL: str = "sqlite:///./dev.db"
    SECRET_KEY=your-secret-key-here (REQUIRED in production)
    DEBUG=True
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


# Default secret key - ONLY for development use
_DEFAULT_SECRET_KEY = "your-secret-key-change-in-production"


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
    # SECRET_KEY must be set via environment variable in production (DEBUG=False)
    SECRET_KEY: str = _DEFAULT_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @model_validator(mode="after")
    def validate_secret_key_in_production(self) -> "Settings":
        """
        Validate that SECRET_KEY is properly configured in production mode.

        Raises:
            ValueError: If SECRET_KEY is the default value when DEBUG=False
        """
        if not self.DEBUG:
            if self.SECRET_KEY == _DEFAULT_SECRET_KEY:
                raise ValueError(
                    "SECURITY ERROR: SECRET_KEY must be set to a secure value in production mode. "
                    "Set the SECRET_KEY environment variable to a strong, unique secret key. "
                    "You can generate one using: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
                )
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECURITY ERROR: SECRET_KEY is too short for production use. "
                    "Use a key of at least 32 characters for adequate security."
                )
        return self

    # Printer
    PRINTER_QUEUE_NAME: str = "ZDesigner GK420t"  # Default Zebra printer name

    # CORS - Configure via environment variable CORS_ORIGINS as comma-separated list
    # Example: CORS_ORIGINS=["http://localhost:3000","https://production.example.com"]
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3008",
        "http://localhost:5173",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT_REQUESTS: int = 100  # Requests per window
    RATE_LIMIT_DEFAULT_WINDOW: int = 60  # Window in seconds

    # Caching
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 300  # 5 minutes default TTL
    CACHE_MAX_SIZE: int = 1000  # Maximum cache entries

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
