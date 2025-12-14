"""Chat Pydantic schemas for AI agent request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """Schema for chat request from frontend."""

    message: str = Field(..., min_length=1, max_length=10000, description="User's chat message")
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID (null for new conversation)")


class ToolCall(BaseModel):
    """Schema for tool call metadata in chat response."""

    tool: str = Field(..., description="Name of the tool that was called")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to the tool")


class ChatResponse(BaseModel):
    """Schema for chat response to frontend."""

    conversation_id: int = Field(..., description="ID of the conversation (newly created or existing)")
    response: str = Field(..., description="AI assistant's response message")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="List of tools invoked during this turn")

    class Config:
        from_attributes = True
