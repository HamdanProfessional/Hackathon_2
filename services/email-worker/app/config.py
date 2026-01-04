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

    # Email Configuration (custom email API)
    EMAIL_KEY: str = Field(default="emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d")
    EMAIL_API_URL: str = Field(default="https://email.testservers.online/api/send")
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
