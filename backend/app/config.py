"""Application configuration settings."""
import os
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsError
from typing import List

# Load .env file manually to ensure it's loaded
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # JWT
    JWT_SECRET_KEY: str = Field(..., min_length=32, description="JWT secret key (minimum 32 characters)")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Better Auth Integration
    # For Better Auth JWT plugin compatibility, BETTER_AUTH_SECRET should match JWT_SECRET_KEY
    # We use a computed property instead of a separate field to avoid circular dependency

    @property
    def BETTER_AUTH_SECRET(self) -> str:
        """Better Auth JWT secret - uses same value as JWT_SECRET_KEY for compatibility."""
        return self.JWT_SECRET_KEY

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,https://frontend-hamdanprofessionals-projects.vercel.app,https://backend-hamdanprofessionals-projects.vercel.app",
        description="Comma-separated list of allowed CORS origins"
    )

    # Application
    APP_NAME: str = "Todo CRUD API"
    DEBUG: bool = True

    # Phase III: AI Agent Configuration (OpenAI primary, Gemini backup)
    # We'll load this from OPENAI_API_KEY first, then GEMINI_API_KEY as fallback
    AI_API_KEY: str = Field(default="", description="OpenAI or Google Gemini API key for AI agent")
    AI_BASE_URL: str = Field(default="https://api.openai.com/v1", description="Base URL for AI API")
    # Use OpenAI model as primary (more reliable)
    AI_MODEL: str = "gpt-4o-mini"  # OpenAI GPT-4o Mini (affordable and fast)
    MAX_TOKENS_PER_DAY: int = 50000  # Rate limiting

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load AI API key from environment variables (priority: Groq -> Gemini -> OpenAI -> Grok)
        self.AI_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROK_API_KEY") or ""

        # Auto-detect and configure AI provider
        if not self.AI_API_KEY:
            print("[WARNING] No API key found - AI features will be disabled")
        elif os.getenv("GROQ_API_KEY"):
            print("[OK] Using Groq API (FREE - 14,400 req/day)")
            self.AI_BASE_URL = "https://api.groq.com/openai/v1"
            # Try llama-3.1-8b-instant which is faster and more reliable
            self.AI_MODEL = "llama-3.1-8b-instant"
        elif os.getenv("GEMINI_API_KEY"):
            print("[OK] Using Gemini API (FREE - 1,500 req/day)")
            self.AI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
            self.AI_MODEL = "gemini-2.5-flash"
        elif os.getenv("OPENAI_API_KEY"):
            print("[OK] Using OpenAI API (Pay-as-you-go)")
            self.AI_BASE_URL = "https://api.openai.com/v1"
            self.AI_MODEL = "gpt-4o-mini"
        elif os.getenv("GROK_API_KEY"):
            print("[OK] Using Grok API (xAI - Requires credits)")
            self.AI_BASE_URL = "https://api.x.ai/v1"
            self.AI_MODEL = "grok-beta"

        # Override DATABASE_URL if it's the default local one
        if self.DATABASE_URL == "postgresql+asyncpg://postgres:2763@localhost:5432/postgres":
            # Try to load from .env file
            from dotenv import load_dotenv
            load_dotenv(override=True)
            self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v or not v.strip():
            raise SettingsError("DATABASE_URL is required and cannot be empty")
        # Allow SQLite for testing
        if os.getenv("TESTING") == "true" and v.startswith("sqlite+aiosqlite"):
            return v
        if not v.startswith(("postgresql://", "postgres://", "postgresql+asyncpg://", "postgres+asyncpg://")):
            raise SettingsError("DATABASE_URL must be a valid PostgreSQL connection string")
        return v

    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v):
        if os.getenv("TESTING") == "true" and v == "test-secret-key-for-testing-purposes-only-32chars":
            return v  # Allow test secret during testing
        if not v or not v.strip():
            raise SettingsError("JWT_SECRET_KEY is required and cannot be empty")
        if len(v) < 32:
            raise SettingsError("JWT_SECRET_KEY must be at least 32 characters long")
        if v in ("your-super-secret-jwt-key-change-this-in-production", "secret", "test"):
            raise SettingsError(
                "JWT_SECRET_KEY must be changed from the default value for security"
            )
        return v

      # Comment out AI_API_KEY validator for now
    # @validator("AI_API_KEY")
    # def validate_ai_key(cls, v):
    #     # Allow empty AI_API_KEY for basic functionality without AI features
    #     if not v or not v.strip():
    #         print("Warning: AI_API_KEY not set - AI features will be disabled")
    #         return ""
    #     if v == "your-gemini-api-key-here":
    #         print("Warning: AI_API_KEY is set to default value - AI features will not work")
    #         return ""
    #     # Gemini API keys are alphanumeric strings, not prefixed with "sk-"
    #     return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {
        "env_file": ".env.test" if os.getenv("TESTING") == "true" else ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra env vars
    }


# Global settings instance
# This will raise SettingsError if required environment variables are missing
try:
    settings = Settings()
    print(f"DEBUG: JWT_SECRET loaded: {settings.JWT_SECRET_KEY[:5]}...")
    print(f"DEBUG: JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    print(f"[AI] AI_MODEL configured: {settings.AI_MODEL}")
except SettingsError as e:
    import sys
    print(f"[ERROR] Configuration Error: {e}", file=sys.stderr)
    print("\nPlease check your .env file and ensure all required environment variables are set.", file=sys.stderr)
    print("\nRequired variables:", file=sys.stderr)
    print("- DATABASE_URL: PostgreSQL database connection string", file=sys.stderr)
    print("- JWT_SECRET_KEY: Secure secret key (min 32 characters)", file=sys.stderr)
    print("- AI_API_KEY: Google Gemini API key (get from https://aistudio.google.com/app/apikey)", file=sys.stderr)
    print("\nExample: generate a secure JWT secret with:", file=sys.stderr)
    print('  openssl rand -base64 32', file=sys.stderr)
    sys.exit(1)
