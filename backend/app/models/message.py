"""Message SQLAlchemy model."""
from datetime import datetime
import uuid as uuid_lib

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Message(Base):
    """Message model for individual messages within conversations."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)  # OpenAI tool_calls format: [{"id": "call_abc", "type": "function", "function": {...}}]
    tool_call_id = Column(String(100), nullable=True)  # For tool role messages - links to assistant's tool_calls[].id
    name = Column(String(100), nullable=True)  # For tool role messages - function name
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system', 'tool')", name="check_role_values"),
        Index("idx_messages_conversation_created", "conversation_id", "created_at"),
    )

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role={self.role}, content={self.content[:50]})>"
