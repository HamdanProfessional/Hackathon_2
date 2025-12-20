"""User Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password must be at least 8 characters long"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's full name"
    )


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    id: str  # UUID as string
    email: str
    name: str
    created_at: datetime
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""

    preferences: Dict[str, Any] = Field(..., description="User preferences as key-value pairs")
