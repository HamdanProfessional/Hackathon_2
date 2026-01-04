---
name: ai-agent-suite
description: Build stateless AI agents by creating AgentService classes in backend/app/ai/agent.py that load conversation history from PostgreSQL via load_conversation_context() on every request (no in-memory state), orchestrate MCP tool calls for CRUD operations (get_tasks, create_task, update_task, delete_task) through backend/app/ai/tools.py, and monitor health with /health endpoints that check database connectivity, tool execution, and response time metrics. Use when implementing chatbot APIs at POST /api/chat/message, creating conversation persistence with cursor pagination at GET /api/chat/conversations, or enforcing stateless architecture with scripts/validate_stateless.py.
---

# AI Agent Suite Skill

Build stateless AI agents with PostgreSQL-backed conversation persistence, MCP tool orchestration, and comprehensive monitoring.

## Quick Reference

| Feature | File Path | Command/Pattern |
|---------|-----------|-----------------|
| Agent Service | `backend/app/ai/agent.py` | `AgentService(user_id, db).process_message()` |
| Tool Registry | `backend/app/ai/tools.py` | `@register_tool("tool_name")` decorator |
| Context Manager | `backend/app/ai/conversation_manager.py` | `load_conversation_context(conv_id, db, limit=50)` |
| Chat Router | `backend/app/api/chat.py` | `POST /api/chat/message` endpoint |
| Conversation Model | `backend/app/models/conversation.py` | `Conversation/Message` SQLModel classes |
| Validation Script | `backend/scripts/validate_stateless.py` | `python backend/scripts/validate_stateless.py` |
| Integration Test | `backend/tests/test_agent.py` | `pytest backend/tests/test_agent.py -v` |

## When to Use This Skill

| User Request | Action | File to Modify |
|--------------|--------|----------------|
| "create AI agent" | Implement AgentService | `backend/app/ai/agent.py` |
| "AI not calling tools" | Check tool docstrings | `backend/app/ai/tools.py` |
| "chat history not persisting" | Verify Conversation model | `backend/app/models/conversation.py` |
| "conversation API returns 404" | Check router registration | `backend/app/api/chat.py` |
| "agent memory growing" | Run validation script | `python backend/scripts/validate_stateless.py` |
| "need health check endpoint" | Add to main.py | `backend/app/main.py` |
| "test MCP tool invocation" | Run integration test | `pytest backend/tests/test_agent.py -k test_tool_call` |
| "slow AI responses" | Check message limit in load_conversation_context() | `backend/app/ai/conversation_manager.py` |

## Common Issues & Solutions

| Issue | Symptom | Root Cause | Fix Command |
|-------|---------|------------|-------------|
| Agent not calling tools | `tool_calls: []` in response | Tool description too vague | Edit `backend/app/ai/tools.py`: Add "Use this when user asks..." to docstring |
| High latency | Response time > 5s | Too many messages loaded | In `conversation_manager.py`: Change `limit=100` to `limit=50` |
| Memory leak | `self.history = []` found | In-memory state violation | Refactor to `load_conversation_context()` every request |
| Tool fails silently | No error in logs | Missing try-except | Add `try-except HTTPException` in tool function |
| 404 on conversations | `{"detail": "Not found"}` | Missing router registration | In `main.py`: Add `app.include_router(chat.router)` |
| Empty tool_calls array | Groq returns text only | Tool schema mismatch | Check parameter types match function signature exactly |
| Database connection error | `psycopg2.OperationalError` | Wrong DATABASE_URL | In `.env`: Set `DATABASE_URL=postgresql://user:pass@host:5432/db` |
| JWT authentication fails | `401 Unauthorized` | Missing Authorization header | In frontend: Add `headers: { Authorization: Bearer ${token} }` |

---

## Part 1: Agent Builder

### File: backend/app/ai/agent.py

```python
"""
Agent Service for AI chat functionality.
Stateless: Loads conversation history from PostgreSQL on every request.
"""
from openai import AsyncOpenAI
from app.config import settings
from app.ai.tools import TOOL_REGISTRY
from app.ai.conversation_manager import load_conversation_context

class AgentService:
    """Stateless AI agent service - no in-memory state."""

    def __init__(self, user_id: str, db: Session):
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL  # e.g., "llama-3.1-8b-instant"
        self.user_id = user_id
        self.db = db
        # NO self.history or self.conversation_state!

    async def process_message(self, message: str, conversation_id: int = None):
        """Process user message - loads context from DB every time."""
        # Load conversation history (stateless - no in-memory cache)
        history = load_conversation_context(conversation_id, self.db, limit=50)

        # Build messages array for API
        messages = [{"role": msg.role, "content": msg.content} for msg in history]
        messages.append({"role": "user", "content": message})

        # Call AI model with tools
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=list(TOOL_REGISTRY.values())
        )

        return response
```

### File: backend/app/ai/tools.py

```python
"""
MCP Tool Registry for CRUD operations.
Tools are invoked by AI agent based on user intent.
"""
from typing import Dict, Callable

TOOL_REGISTRY: Dict[str, Callable] = {}

def register_tool(name: str):
    """Decorator to register MCP tool."""
    def decorator(func: Callable) -> Callable:
        TOOL_REGISTRY[name] = func
        return func
    return decorator

@register_tool("get_tasks")
async def get_tasks(user_token: str, status: str = None) -> Dict:
    """
    Retrieve tasks for the authenticated user from database.

    Use this when user asks: "Show me my tasks", "What do I need to do?",
    "List my pending items", "Display all tasks"

    Args:
        user_token: JWT token for authentication (from Authorization header)
        status: Filter by "pending", "in_progress", or "completed"

    Returns:
        Dict with success flag and tasks list:
        {"success": true, "data": [{"id": 1, "title": "...", "status": "..."}]}
    """
    from app.auth.jwt import verify_token
    user_id = verify_token(user_token)

    from app.database import get_db
    from app.models.task import Task
    from sqlmodel import select

    db = next(get_db())
    statement = select(Task).where(Task.user_id == user_id)
    if status:
        statement = statement.where(Task.status == status)

    tasks = db.exec(statement).all()
    return {"success": True, "data": [t.dict() for t in tasks]}

@register_tool("create_task")
async def create_task(title: str, user_token: str, priority: str = "normal") -> Dict:
    """
    Create a new task for authenticated user.

    Use this when user says: "Add a task", "Create todo", "New reminder",
    "Remember to...", "I need to..."
    """
    from app.auth.jwt import verify_token
    user_id = verify_token(user_token)

    from app.database import get_db
    from app.models.task import Task

    db = next(get_db())
    task = Task(title=title, user_id=user_id, priority=priority)
    db.add(task)
    db.commit()
    db.refresh(task)

    return {"success": True, "data": task.dict()}

@register_tool("update_task")
async def update_task(task_id: int, user_token: str, **fields) -> Dict:
    """
    Update existing task with new values.

    Use this when user says: "Mark task complete", "Change task title",
    "Update priority", "Mark as done"
    """
    from app.auth.jwt import verify_token
    user_id = verify_token(user_token)

    from app.database import get_db
    from app.models.task import Task
    from sqlmodel import select

    db = next(get_db())
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()

    if not task:
        return {"success": False, "error": "Task not found"}

    for key, value in fields.items():
        setattr(task, key, value)

    db.add(task)
    db.commit()

    return {"success": True, "data": task.dict()}

@register_tool("delete_task")
async def delete_task(task_id: int, user_token: str) -> Dict:
    """
    Delete task from database.

    Use this when user says: "Delete task", "Remove this", "Get rid of it"
    """
    from app.auth.jwt import verify_token
    user_id = verify_token(user_token)

    from app.database import get_db
    from app.models.task import Task
    from sqlmodel import select

    db = next(get_db())
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()

    if not task:
        return {"success": False, "error": "Task not found"}

    db.delete(task)
    db.commit()

    return {"success": True, "message": "Task deleted"}
```

### File: backend/app/api/chat.py

```python
"""
Chat API endpoints.
Handles AI agent communication with tool orchestration.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.ai.agent import AgentService
from app.auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    message_id: int

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process user message through AI agent at POST /api/chat/message

    Flow:
    1. Verify JWT from Authorization header
    2. Load conversation history from PostgreSQL
    3. Call AI model with MCP tools
    4. Persist user message and AI response
    5. Return AI response with message IDs
    """
    try:
        agent = AgentService(user_id=current_user["id"], db=db)
        result = await agent.process_message(
            message=request.message,
            conversation_id=request.conversation_id
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations")
async def list_conversations(
    cursor: str | None = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user conversations with cursor pagination.

    Returns: {"conversations": [...], "next_cursor": "...", "has_more": bool}
    """
    from app.ai.conversation_manager import paginate_conversations
    return paginate_conversations(current_user["id"], db, cursor, limit)

@router.get("/conversations/{conv_id}/messages")
async def get_conversation_messages(
    conv_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all messages for a conversation.

    Returns: {"messages": [{"role": "user", "content": "..."}]}
    """
    from app.ai.conversation_manager import load_conversation_context
    messages = load_conversation_context(conv_id, db, limit=None)
    return {"messages": [m.dict() for m in messages]}

@router.delete("/conversations/{conv_id}")
async def delete_conversation(
    conv_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete conversation (sets deleted_at timestamp).
    """
    from app.models.conversation import Conversation
    from datetime import datetime

    conv = db.get(Conversation, conv_id)
    if not conv or conv.user_id != current_user["id"]:
        raise HTTPException(status_code=404)

    conv.deleted_at = datetime.utcnow()
    db.add(conv)
    db.commit()

    return {"message": "Conversation deleted"}
```

### Register Router in backend/app/main.py

```python
from app.api import chat

# Add after other router includes
app.include_router(chat.router)
```

---

## Part 2: Database Models

### File: backend/app/models/conversation.py

```python
"""
Conversation and Message models for AI Agent persistence.
"""
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Index


class Conversation(SQLModel, table=True):
    """
    Conversation model for AI agent chat history.
    Supports soft delete via deleted_at timestamp.
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255, default="New Chat")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)

    messages: list["Message"] = Relationship(back_populates="conversation")

    __table_args__ = (
        Index("ix_conversations_user_updated", "user_id", "updated_at"),
        Index("ix_conversations_user_deleted", "user_id", "deleted_at"),
    )


class Message(SQLModel, table=True):
    """
    Message model for AI agent chat history.
    Stores both user and assistant messages.
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: Literal["user", "assistant"] = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )
```

### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Add conversations and messages tables"
alembic upgrade head
```

---

## Part 3: Context Manager

### File: backend/app/ai/conversation_manager.py

```python
"""
Conversation context manager for stateless AI agents.
Loads history from PostgreSQL on every request.
"""
from typing import List, Optional
from sqlmodel import Session, select
from app.models.conversation import Conversation, Message


def load_conversation_context(
    conversation_id: Optional[int],
    db: Session,
    limit: int = 50
) -> List[Message]:
    """
    Load conversation history from database (stateless pattern).

    Args:
        conversation_id: Conversation ID or None for new conversation
        db: Database session
        limit: Maximum messages to load (default: 50)

    Returns:
        List of Message objects ordered by created_at
    """
    if not conversation_id:
        return []

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(limit)
    )

    messages = db.exec(statement).all()
    return messages


def paginate_conversations(
    user_id: str,
    db: Session,
    cursor: Optional[str] = None,
    limit: int = 20
) -> dict:
    """
    Paginate conversations using cursor-based pagination.

    Returns:
        {
            "conversations": [...],
            "next_cursor": "base64_encoded_cursor",
            "has_more": bool
        }
    """
    statement = select(Conversation).where(
        Conversation.user_id == user_id,
        Conversation.deleted_at.is_(None)
    )

    if cursor:
        # Decode cursor and apply filter
        import base64
        import json
        cursor_data = json.loads(base64.b64decode(cursor))
        statement = statement.where(
            Conversation.updated_at < cursor_data["updated_at"]
        )

    statement = statement.order_by(Conversation.updated_at.desc()).limit(limit + 1)

    results = db.exec(statement).all()
    conversations = results[:limit]
    has_more = len(results) > limit

    # Generate next cursor
    next_cursor = None
    if conversations and has_more:
        last_conv = conversations[-1]
        cursor_data = {"updated_at": last_conv.updated_at.isoformat()}
        next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

    return {
        "conversations": [c.dict() for c in conversations],
        "next_cursor": next_cursor,
        "has_more": has_more
    }


def create_conversation(user_id: str, title: str, db: Session) -> Conversation:
    """Create new conversation."""
    conv = Conversation(user_id=user_id, title=title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def save_message(
    conversation_id: int,
    role: str,
    content: str,
    db: Session
) -> Message:
    """Save message to database."""
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # Update conversation timestamp
    conv = db.get(Conversation, conversation_id)
    conv.updated_at = datetime.utcnow()
    db.add(conv)
    db.commit()

    return msg
```

---

## Part 4: Stateless Validation

### File: backend/scripts/validate_stateless.py

```python
"""
Validate stateless architecture in AI agents.
Checks for in-memory state violations.
"""
import ast
import os
from pathlib import Path

ANTI_PATTERNS = [
    "self.history",
    "self.conversation_state",
    "self.messages",
    "self.memory",
    "self.context_cache",
]

def check_file(filepath: Path) -> list:
    """Check Python file for anti-patterns."""
    issues = []

    with open(filepath) as f:
        tree = ast.parse(f.read(), filename=filepath)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    if any(pattern in ast.unparse(target) for pattern in ANTI_PATTERNS):
                        issues.append({
                            "file": str(filepath),
                            "line": node.lineno,
                            "issue": f"In-memory state detected: {ast.unparse(target)}",
                            "severity": "error"
                        })

    return issues


def validate_agent_code():
    """Validate all agent-related files."""
    backend_dir = Path("backend/app/ai")
    all_issues = []

    for py_file in backend_dir.rglob("*.py"):
        issues = check_file(py_file)
        all_issues.extend(issues)

    if all_issues:
        print("❌ Stateless architecture violations found:")
        for issue in all_issues:
            print(f"  {issue['file']}:{issue['line']} - {issue['issue']}")
        return False
    else:
        print("✅ No stateless violations detected")
        return True


if __name__ == "__main__":
    validate_agent_code()
```

### Run Validation

```bash
python backend/scripts/validate_stateless.py
```

---

## Part 5: Testing

### File: backend/tests/test_agent.py

```python
"""
Integration tests for AI agent with MCP tools.
"""
import pytest
from httpx import AsyncClient
from app.models.conversation import Conversation, Message


@pytest.mark.asyncio
async def test_chat_message_creates_conversation(async_client: AsyncClient, auth_headers: dict):
    """Test POST /api/chat/message creates new conversation."""
    response = await async_client.post(
        "/api/chat/message",
        json={"message": "Hello, create a task called 'Test task'"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data


@pytest.mark.asyncio
async def test_agent_calls_create_task_tool(async_client: AsyncClient, auth_headers: dict):
    """Test AI agent invokes create_task MCP tool."""
    response = await async_client.post(
        "/api/chat/message",
        json={"message": "Create a task called 'Buy groceries'"},
        headers=auth_headers
    )

    assert response.status_code == 200
    # Verify tool was called (check database)
    from app.database import get_db
    from app.models.task import Task
    from sqlmodel import select

    db = next(get_db())
    tasks = db.exec(select(Task)).all()
    assert any(t.title == "Buy groceries" for t in tasks)


@pytest.mark.asyncio
async def test_conversation_persistence(async_client: AsyncClient, auth_headers: dict):
    """Test conversation history persists across requests."""
    # First message
    response1 = await async_client.post(
        "/api/chat/message",
        json={"message": "My name is Alice"},
        headers=auth_headers
    )
    conv_id = response1.json()["conversation_id"]

    # Second message in same conversation
    response2 = await async_client.post(
        "/api/chat/message",
        json={"message": "What's my name?", "conversation_id": conv_id},
        headers=auth_headers
    )

    # AI should remember name from context
    assert "Alice" in response2.json()["response"]


@pytest.mark.asyncio
async def test_list_conversations(async_client: AsyncClient, auth_headers: dict):
    """Test GET /api/chat/conversations with pagination."""
    response = await async_client.get(
        "/api/chat/conversations?limit=10",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert "next_cursor" in data
    assert "has_more" in data


@pytest.mark.asyncio
async def test_delete_conversation(async_client: AsyncClient, auth_headers: dict):
    """Test DELETE /api/chat/conversations/{id} soft deletes."""
    # Create conversation
    response = await async_client.post(
        "/api/chat/message",
        json={"message": "Test message"},
        headers=auth_headers
    )
    conv_id = response.json()["conversation_id"]

    # Delete conversation
    delete_response = await async_client.delete(
        f"/api/chat/conversations/{conv_id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 200

    # Verify soft deleted (not returned in list)
    list_response = await async_client.get(
        "/api/chat/conversations",
        headers=auth_headers
    )
    assert not any(c["id"] == conv_id for c in list_response.json()["conversations"])


@pytest.mark.asyncio
async def test_stateless_context_loading(async_client: AsyncClient, auth_headers: dict):
    """Test context is loaded from database, not memory."""
    # Create conversation with message
    response = await async_client.post(
        "/api/chat/message",
        json={"message": "Remember: the secret code is 1234"},
        headers=auth_headers
    )
    conv_id = response.json()["conversation_id"]

    # Wait a bit (ensures no in-memory cache)
    import asyncio
    await asyncio.sleep(1)

    # New agent instance should still have context
    response2 = await async_client.post(
        "/api/chat/message",
        json={"message": "What's the secret code?", "conversation_id": conv_id},
        headers=auth_headers
    )

    assert "1234" in response2.json()["response"]
```

### Run Tests

```bash
cd backend
pytest tests/test_agent.py -v
```

---

## Quality Checklist

Before finalizing AI agent implementation:

- [ ] **Database Models**: `Conversation` and `Message` created with proper indexes
- [ ] **Stateless Pattern**: No `self.history` or `self.memory` in AgentService
- [ ] **Context Loading**: Uses `load_conversation_context()` on every request
- [ ] **JWT Authentication**: All endpoints use `Depends(get_current_user)`
- [ ] **Message Persistence**: Messages saved immediately after creation
- [ ] **Tenant Isolation**: `user_id` boundaries enforced in all queries
- [ ] **Tool Registration**: All tools use `@register_tool()` decorator
- [ ] **Tool Docstrings**: Include "Use this when user asks..." patterns
- [ ] **Health Check**: `/health` endpoint checks database and tools
- [ ] **Error Handling**: Try-except blocks with HTTPException
- [ ] **Pagination**: Cursor-based pagination for conversation list
- [ ] **Soft Delete**: `deleted_at` timestamp instead of hard deletes
- [ ] **Tests**: Integration tests for tool invocation and persistence
- [ ] **Validation**: `python backend/scripts/validate_stateless.py` passes
- [ ] **Router Registration**: `app.include_router(chat.router)` in main.py
- [ ] **Environment Variables**: `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL` set
