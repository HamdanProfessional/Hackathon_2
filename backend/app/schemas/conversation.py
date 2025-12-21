"""Conversation Pydantic schemas for request/response validation."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ConversationResponse(BaseModel):
    """Schema for conversation data in responses."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
