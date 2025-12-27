"""Email Worker Configuration."""
import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Email Worker Settings."""

    # Application
    APP_NAME: str = "Email Worker"
    DEBUG: bool = False

    # Email Configuration (Gmail SMTP)
    MAIL_SERVER: str = Field(default="smtp.gmail.com")
    MAIL_PORT: int = Field(default=587)
    MAIL_USE_TLS: bool = Field(default=True)
    MAIL_USERNAME: str = Field(default="")
    MAIL_PASSWORD: str = Field(default="")
    MAIL_FROM: str = Field(default="noreply@hackathon2.testservers.online")
    MAIL_FROM_NAME: str = Field(default="Todo App")

    # Database
    DATABASE_URL: str = Field(...)

    # Dapr Configuration
    DAPR_HTTP_HOST: str = "localhost"
    DAPR_HTTP_PORT: str = "3500"
    DAPR_PUBSUB_NAME: str = "todo-pubsub"

    model_config = {"case_sensitive": True, "extra": "ignore"}


settings = Settings()
