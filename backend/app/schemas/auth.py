"""Authentication Pydantic schemas."""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User password"
    )


class TokenResponse(BaseModel):
    """Schema for token response after login/register."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
