# AI Agent Suite - Reusable Templates

## Agent Service Template

```python
# backend/app/ai/agent.py
from openai import AsyncOpenAI
from sqlmodel import Session, select
from app.models import Conversation, Message
from app.config import settings

class AgentService:
    """Stateless AI agent template."""

    def __init__(self, user_id: str, db: Session):
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL
        self.user_id = user_id
        self.db = db

    async def process_message(
        self,
        message: str,
        conversation_id: int | None = None
    ) -> dict:
        """Process message with stateless architecture."""
        # 1. Load history from database
        history = self._load_history(conversation_id)

        # 2. Build messages
        messages = [
            {"role": m.role, "content": m.content}
            for m in history
        ]
        messages.append({"role": "user", "content": message})

        # 3. Call AI
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        # 4. Save response
        # ... save to database

        return {"response": response.choices[0].message.content}

    def _load_history(self, conversation_id: int | None) -> list[Message]:
        """Load conversation history - ALWAYS from database."""
        if not conversation_id:
            return []

        return self.db.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(50)
        ).all()
```

## MCP Tool Template

```python
# backend/app/ai/tools.py
from typing import Dict, Any
from app.auth import verify_token

def tool_function(
    user_token: str,
    required_param: str,
    optional_param: str | None = None
) -> Dict[str, Any]:
    """
    Brief description of what tool does.

    Detailed explanation for AI understanding.

    Args:
        user_token: JWT authentication token
        required_param: Description of required parameter
        optional_param: Description of optional parameter

    Returns:
        Description of return value
    """
    try:
        user_id = verify_token(user_token)
        # ... tool logic
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Database Models Template

```python
# backend/app/models/conversation.py
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Index

class Conversation(SQLModel, table=True):
    """Conversation model for AI chat."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    messages: list["Message"] = Relationship(back_populates="conversation")

    __table_args__ = (
        Index("ix_conversations_user_updated", "user_id", "updated_at"),
    )

class Message(SQLModel, table=True):
    """Message model for AI chat."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(nullable=False)  # "user" or "assistant"
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )
```

## FastAPI Router Template

```python
# backend/app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from app.ai.agent import AgentService
from app.database import get_session
from app.auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Process chat message with AI agent."""
    agent = AgentService(user_id=current_user["id"], db=db)
    result = await agent.process_message(
        message=request.message,
        conversation_id=request.conversation_id
    )
    return result
```

## Migration Template

```python
# alembic/versions/xxx_add_conversations.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_user_updated', 'conversations',
                    ['user_id', 'updated_at'])

def downgrade():
    op.drop_table('conversations')
```

## Test Template

```python
# tests/test_ai_agent.py
import pytest
from app.ai.agent import AgentService

def test_stateless_agent(db_session, test_user):
    """Verify agent loads from database each request."""
    agent1 = AgentService(user_id=test_user.id, db=db_session)
    agent2 = AgentService(user_id=test_user.id, db=db_session)

    # Both should load from DB, not share state
    # This validates stateless architecture

@pytest.mark.asyncio
async def test_process_message(db_session, test_user):
    """Test message processing with AI."""
    agent = AgentService(user_id=test_user.id, db=db_session)
    result = await agent.process_message("Hello!")

    assert "response" in result
    assert result["response"]
```
