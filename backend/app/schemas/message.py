"""Message Pydantic schemas for request/response validation."""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


class MessageResponse(BaseModel):
    """Schema for message data in responses."""

    role: Literal["user", "assistant"] = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Timestamp when message was created")

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
