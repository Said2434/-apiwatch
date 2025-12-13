"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str
    ASYNC_DATABASE_URL: str

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str

    # Application
    APP_NAME: str = "APIWatch"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Health Check Defaults
    DEFAULT_CHECK_INTERVAL: int = 60  # seconds
    DEFAULT_TIMEOUT: int = 10  # seconds
    MAX_RETRIES: int = 3

    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
