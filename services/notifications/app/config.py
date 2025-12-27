"""Application configuration settings for notification service."""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

# Load .env file manually
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database - shared with main backend
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # Dapr Configuration
    DAPR_HTTP_HOST: str = "localhost"
    DAPR_HTTP_PORT: str = "3500"
    DAPR_PUBSUB_NAME: str = "todo-pubsub"
    DAPR_ENABLED: bool = True

    # Notification Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@todoapp.com"
    EMAIL_ENABLED: bool = False

    # Worker Settings
    DUE_CHECK_INTERVAL_SECONDS: int = 3600  # 1 hour
    RECURRING_CHECK_INTERVAL_SECONDS: int = 3600  # 1 hour
    DUE_THRESHOLD_HOURS: int = 24  # Notify for tasks due within 24 hours

    # Application
    APP_NAME: str = "Notification Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "local"  # local, staging, production

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Override DATABASE_URL if it's the default local one
        if self.DATABASE_URL == "postgresql+asyncpg://postgres:2763@localhost:5432/postgres":
            load_dotenv(override=True)
            self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        origins = os.getenv("CORS_ORIGINS", "")
        return [origin.strip() for origin in origins.split(",") if origin.strip()]

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Global settings instance
try:
    settings = Settings()
    print(f"[Notification Service] Configuration loaded successfully")
    print(f"[Notification Service] Dapr enabled: {settings.DAPR_ENABLED}")
    print(f"[Notification Service] Email enabled: {settings.EMAIL_ENABLED}")
except Exception as e:
    import sys
    print(f"[ERROR] Configuration Error: {e}", file=sys.stderr)
    sys.exit(1)
