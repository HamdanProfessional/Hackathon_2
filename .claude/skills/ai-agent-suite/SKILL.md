---
name: ai-agent-suite
description: Comprehensive AI agent suite covering agent building (AsyncOpenAI with Google Gemini), orchestration (database context, JWT auth, session management), conversation history (pagination, soft delete, stateless patterns), and monitoring (health checks, performance metrics, error analysis).
version: 2.0.0
category: ai-agents
tags: [agents, ai, orchestration, monitoring, gemini, openai, stateless-agents, mcp, chatkit]
dependencies: [openai, dapr-python, fastapi, sqlmodel]
---

# AI Agent Suite Skill

Comprehensive AI agent development, orchestration, conversation history management, and monitoring.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | Basic agent, chat integration, best practices |
| Scripts | `scripts/` | `test_agent.py`, `validate_conversation.py` |
| Templates | `references/templates.md` | Reusable code templates |
| Links | `references/links.md` | External documentation |

## When to Use This Skill

Use this skill when:
- Creating stateless AI agents with database context
- Implementing agent orchestration with JWT authentication
- Managing conversation history with cursor-based pagination
- Setting up conversation persistence and soft delete
- Integrating MCP tools with agents
- Managing agent sessions
- Analyzing agent metrics and errors

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent not calling tools | Tool schema incorrect | Check tool descriptions and parameter types |
| High latency | Too many messages in history | Limit to 50 messages, use index optimization |
| Memory growing | In-memory state detected | Run `validate_conversation.py` to find violations |
| Tool fails silently | Missing error handling | Add try-catch blocks in tool execution |

---

## Part 1: Agent Builder

### Quick Start

Create AI agent with AsyncOpenAI and Gemini:

```python
from openai import AsyncOpenAI
from app.config import settings

class AgentService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL
```

See `examples/basic-agent.md` for complete implementation.

### MCP Tools Integration

Integrate tools in `backend/app/ai/tools.py`:
- `add_task` - Create new tasks
- `list_tasks` - Retrieve and filter
- `complete_task` - Mark as complete
- `update_task` - Modify details
- `delete_task` - Remove with confirmation

### Chat Endpoint Implementation

```python
"""
Chat endpoint implementation for AI agent.
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
    """Process user message through AI agent."""
    try:
        # Initialize agent with user context
        agent = AgentService(
            user_id=current_user["id"],
            db=db
        )

        # Process message
        result = await agent.process_message(
            message=request.message,
            conversation_id=request.conversation_id
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            message_id=result["message_id"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Part 2: Agent Orchestrator

### When to Use

- User asks to "create an AI agent" or "wire up an agent"
- Building stateless AI assistants that need database access
- Integrating agents with FastAPI backend and MCP tools
- Setting up conversation persistence and chat history

### Database Models

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
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)

    messages: list["Message"] = Relationship(back_populates="conversation")

    __table_args__ = (
        Index("ix_conversations_user_updated", "user_id", "updated_at"),
    )


class Message(SQLModel, table=True):
    """
    Message model for AI agent chat history.
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

See `examples/chat-integration.md` for complete orchestrator implementation.

---

## Part 3: Conversation History Management

### Stateless Context Loading

```python
from app.agents.context_manager import load_conversation_context

async def run_agent(conversation_id: str, user_message: str, db: Session):
    # Load last 50 messages (stateless - fetch from DB every request)
    history = load_conversation_context(conversation_id, db, limit=50)

    # Build messages for AI
    messages = [{"role": msg.role, "content": msg.content} for msg in history]
    messages.append({"role": "user", "content": user_message})

    # Call AI model with full context
    response = await ai_client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response
```

### Cursor-Based Pagination

```python
from app.utils.pagination import paginate_conversations

@router.get("/api/chat/conversations")
async def list_conversations(
    cursor: str | None = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    result = paginate_conversations(
        user_id=current_user.id,
        db=db,
        cursor=cursor,
        limit=limit
    )

    return result  # {"conversations": [...], "cursor": "...", "has_more": bool}
```

### Soft Delete Pattern

```python
from datetime import datetime

@router.delete("/api/chat/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    conversation = db.get(Conversation, conversation_id)

    # Validate ownership
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404)

    # Soft delete (set timestamp)
    conversation.deleted_at = datetime.utcnow()
    db.add(conversation)
    db.commit()

    return {"message": "Conversation deleted"}
```

---

## Part 4: Agent Monitoring

### Health Check Implementation

```python
async def perform_health_check():
    checks = {
        "database": await check_database_health(),
        "api_endpoints": await check_api_endpoints(),
        "tool_execution": await test_tool_execution(),
        "memory_usage": check_memory_usage(),
        "cache_system": await check_cache_health()
    }

    overall_status = "healthy" if all(checks.values()) else "degraded"
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Performance Metrics Collection

```python
async def collect_performance_metrics(duration):
    metrics = {
        "response_times": await get_response_time_stats(duration),
        "tool_performance": await get_tool_performance_stats(),
        "conversation_metrics": await get_conversation_metrics(),
        "error_rates": await calculate_error_rates(duration)
    }
    return analyze_and_format_metrics(metrics)
```

### Error Analysis

```python
async def analyze_errors(time_range):
    errors = await fetch_error_logs(time_range)

    analysis = {
        "total_errors": len(errors),
        "error_types": categorize_errors(errors),
        "trending_errors": identify_trends(errors),
        "critical_errors": filter_critical_errors(errors),
        "recommendations": generate_error_recommendations(errors)
    }

    return analysis
```

---

## Quality Checklist

Before finalizing:
- [ ] Database models created with proper indexes
- [ ] AgentOrchestrator class implements stateless pattern
- [ ] JWT authentication enforced in all methods
- [ ] Messages persisted immediately after creation
- [ ] Conversation history retrieved from database
- [ ] User_id boundaries enforced (tenant isolation)
- [ ] Health checks implemented
- [ ] Performance metrics collected
- [ ] Error analysis automated
- [ ] MCP tools registered
- [ ] ChatKit frontend can retrieve history
- [ ] Run `scripts/validate_conversation.py` to check for stateful patterns
- [ ] Run `scripts/test_agent.py` to verify functionality
