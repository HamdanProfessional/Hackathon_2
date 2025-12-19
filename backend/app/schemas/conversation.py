"""Conversation Pydantic schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel


class ConversationResponse(BaseModel):
    """Schema for conversation data in responses."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
