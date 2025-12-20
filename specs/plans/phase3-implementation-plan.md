# Implementation Plan: Phase III - AI Chatbot (Python Agent Architecture)

**Spec**: @specs/features/phase3-ai-chatbot.md
**Phase**: III (AI-Augmented Web App)
**Estimated Complexity**: Complex
**Timeline**: 8-9 days

---

## Overview

Re-implement Phase III AI Chatbot using Python-based agent architecture with **Gemini 2.5 Flash**. This plan eliminates all React ChatKit dependencies and establishes Python as the core chat engine using:
- **openai** SDK (AsyncOpenAI) for Gemini API calls
- **mcp** SDK with **FastMCP** pattern for tool registration
- **Stateless agent** that reconstructs state from Neon DB on every request
- **Custom React widget** built with shadcn/ui and lucide-react
- **Nebula 2025 styling** (dark theme with glass-morphism)

**Success Criteria**:
- [ ] Backend uses `openai>=1.0` with Gemini 2.5 Flash
- [ ] FastMCP server with 5 tools (add/list/complete/update/delete tasks)
- [ ] Messages table stores `tool_calls` JSON for state reconstruction
- [ ] Custom React chat widget (NO @openai/chatkit-react)
- [ ] `/api/chat` endpoint with streaming support
- [ ] Nebula 2025 styling applied
- [ ] User can manage tasks via natural language

---

## Architecture

### System Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 14)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CustomChatWidget.tsx (shadcn/ui + lucide-react)    │   │
│  │  - Message display (user/assistant bubbles)         │   │
│  │  - Input with send button                           │   │
│  │  - Nebula 2025 styling (dark/glass)                 │   │
│  │  - Auto-scroll, loading states                      │   │
│  └───────────────────┬─────────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────┘
                         │ POST /api/chat {message, conversation_id}
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + Python)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  /api/chat Router (app/api/chat.py)                 │   │
│  │  - JWT authentication (get_current_user)            │   │
│  │  - Validates request                                │   │
│  └───────────────────┬─────────────────────────────────┘   │
│                      │                                       │
│  ┌───────────────────▼─────────────────────────────────┐   │
│  │  AgentRunner (app/ai/agent.py)                      │   │
│  │  - Load conversation history from DB                │   │
│  │  - Call Gemini 2.5 Flash via AsyncOpenAI            │   │
│  │  - Execute tool loop (if tool_calls present)        │   │
│  │  - Save messages to DB (including tool_calls JSON)  │   │
│  └───────────────┬──────────────────┬──────────────────┘   │
│                  │                  │                        │
│  ┌───────────────▼──────────┐  ┌───▼──────────────────┐   │
│  │  FastMCP Server          │  │  Neon PostgreSQL       │   │
│  │  (app/ai/mcp_server.py)  │  │  - conversations       │   │
│  │  - add_task()            │  │  - messages (w/ JSON)  │   │
│  │  - list_tasks()          │  │  - tasks               │   │
│  │  - complete_task()       │  │  - users               │   │
│  │  - update_task()         │  └────────────────────────┘   │
│  │  - delete_task()         │                               │
│  └──────────────────────────┘                               │
└──────────────────────────────────────────────────────────────┘
                         │
                         ↓
              Gemini 2.5 Flash API
     (https://generativelanguage.googleapis.com/v1beta/openai/)
```

### Component Responsibilities

**1. Frontend - CustomChatWidget**:
- **Location**: `frontend/components/chat/custom-chat-widget.tsx`
- **Responsibility**: Render chat UI, handle user input, display messages
- **Dependencies**: shadcn/ui components, apiClient
- **Key Features**:
  - Message bubbles (user: gradient, assistant: glass)
  - Input with keyboard support (Enter to send)
  - Auto-scroll to latest message
  - Loading spinner during API calls
  - Nebula 2025 styling (dark/glass-morphism)

**2. Backend - Chat API Router**:
- **Location**: `backend/app/api/chat.py`
- **Responsibility**: Handle chat requests, authentication, conversation CRUD
- **Dependencies**: AgentRunner, JWT auth, database session
- **Endpoints**:
  - `POST /api/chat` - Send message, get AI response
  - `GET /api/chat/conversations` - List user conversations
  - `GET /api/chat/conversations/{id}` - Get conversation history
  - `DELETE /api/chat/conversations/{id}` - Delete conversation

**3. Backend - AgentRunner**:
- **Location**: `backend/app/ai/agent.py`
- **Responsibility**: Stateless agent orchestration
- **Dependencies**: AsyncOpenAI, FastMCP tools, Conversation/Message models
- **Key Methods**:
  - `run(user_id, message, conversation_id)` - Main entry point
  - `_load_message_history(conversation_id)` - Reconstruct OpenAI messages format from DB
  - `_execute_tools(tool_calls, user_id)` - Run MCP tools, return tool response messages
  - `_save_messages(...)` - Persist messages with tool_calls JSON

**4. Backend - FastMCP Server**:
- **Location**: `backend/app/ai/mcp_server.py`
- **Responsibility**: Tool definitions for agent
- **Pattern**: FastMCP global initialization
- **Tools**: add_task, list_tasks, complete_task, update_task, delete_task
- **All tools accept**: `user_id` parameter for isolation

**5. Database - Conversations & Messages**:
- **Location**: `backend/app/models/conversation.py`, `backend/app/models/message.py`
- **Responsibility**: Persist chat history
- **Critical**: Messages table must store `tool_calls` JSON for stateless reconstruction

---

## Data Model Updates

### Current Issues
1. **Conversation.id**: Currently `Integer`, spec requires `UUID`
2. **Conversation**: Missing `title` field
3. **Message**: Missing `tool_calls`, `tool_call_id`, `name` fields
4. **Message.role**: Constraint only allows 'user'/'assistant', needs 'system' and 'tool'

### Required Schema Changes

#### Conversations Table (UPDATE)

| Column | Current | Required | Change |
|--------|---------|----------|--------|
| id | Integer PK | UUID PK | **Change type** |
| user_id | UUID FK | UUID FK | ✓ (no change) |
| title | ❌ Missing | String(200) | **Add field** |
| created_at | DateTime | DateTime | ✓ (no change) |
| updated_at | DateTime | DateTime | ✓ (no change) |

**New Indexes**:
- `created_at DESC` for recent conversations list

#### Messages Table (UPDATE)

| Column | Current | Required | Change |
|--------|---------|----------|--------|
| id | Integer PK | UUID PK | **Change type** |
| conversation_id | Integer FK | UUID FK | **Change type** |
| role | String(20) | Enum['user','assistant','system','tool'] | **Update constraint** |
| content | Text | Text | ✓ (no change) |
| tool_calls | ❌ Missing | JSON (nullable) | **Add field** |
| tool_call_id | ❌ Missing | String(100, nullable) | **Add field** |
| name | ❌ Missing | String(100, nullable) | **Add field** |
| created_at | DateTime | DateTime | ✓ (no change) |

**tool_calls Field Format** (CRITICAL):
```json
[
  {
    "id": "call_abc123",
    "type": "function",
    "function": {
      "name": "add_task",
      "arguments": "{\"user_id\": \"uuid-string\", \"title\": \"Buy groceries\"}"
    }
  }
]
```

**New Indexes**:
- `(conversation_id, created_at ASC)` - Chronological message retrieval
- `role` - Filter by message type

---

## API Design

### 1. Send Chat Message

```http
POST /api/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

Request:
{
  "message": "Add a task to buy groceries with high priority",
  "conversation_id": "uuid-or-null"
}

Response 200 (Non-Streaming):
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I've added 'Buy groceries' to your tasks with high priority. Is there anything else you'd like me to help you with?"
}

Response 200 (Streaming - Optional):
Content-Type: text/event-stream

data: {"type": "chunk", "content": "I've "}
data: {"type": "chunk", "content": "added "}
...
data: {"type": "done", "conversation_id": "uuid"}

Errors:
- 400: Invalid message (empty, too long)
- 401: Unauthorized (missing/invalid JWT)
- 404: Conversation not found or not owned by user
- 500: Agent execution error (Gemini API failure, tool error)
```

### 2. List Conversations

```http
GET /api/chat/conversations?limit=20&offset=0
Authorization: Bearer <jwt_token>

Response 200:
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Task Management Discussion",
      "created_at": "2025-12-15T10:00:00Z",
      "updated_at": "2025-12-15T11:30:00Z",
      "message_count": 8
    }
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

### 3. Get Conversation History

```http
GET /api/chat/conversations/{conversation_id}
Authorization: Bearer <jwt_token>

Response 200:
{
  "id": "uuid",
  "title": "Task Management Discussion",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "Show me high priority tasks",
      "created_at": "2025-12-15T10:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Here are your high priority tasks:\n1. Submit report\n2. Call client",
      "tool_calls": [...],
      "created_at": "2025-12-15T10:00:05Z"
    }
  ]
}

Errors:
- 401: Unauthorized
- 403: Forbidden (not your conversation)
- 404: Not found
```

### 4. Delete Conversation

```http
DELETE /api/chat/conversations/{conversation_id}
Authorization: Bearer <jwt_token>

Response 204: No Content

Errors:
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
```

---

## Implementation Tasks

### Task 1: Update Database Models for tool_calls Support
**Complexity**: Moderate
**Dependencies**: None
**Estimated Time**: 4 hours

**Acceptance Criteria**:
- [ ] Update `Conversation` model to use UUID primary key
- [ ] Add `title` field to `Conversation` (default: "New Conversation")
- [ ] Update `Message` model to use UUID primary key
- [ ] Add `tool_calls` JSON field to `Message` (nullable)
- [ ] Add `tool_call_id` String(100) field to `Message` (nullable)
- [ ] Add `name` String(100) field to `Message` (nullable)
- [ ] Update `role` check constraint to include 'system' and 'tool'
- [ ] Add composite index `(conversation_id, created_at ASC)` on messages
- [ ] Add index on `conversations.created_at DESC`

**Files**:
- `backend/app/models/conversation.py`
- `backend/app/models/message.py`

**Implementation Notes**:
```python
# backend/app/models/conversation.py
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False, default="New Conversation")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_conversations_user_created', 'user_id', 'created_at'),
    )

# backend/app/models/message.py
from sqlalchemy.dialects.postgresql import UUID, JSON

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)  # CRITICAL: OpenAI tool_calls format
    tool_call_id = Column(String(100), nullable=True)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system', 'tool')", name="check_role_values"),
        Index('idx_messages_conversation_created', 'conversation_id', 'created_at'),
    )
```

---

### Task 2: Create Alembic Migration for Schema Changes
**Complexity**: Moderate
**Dependencies**: Task 1
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Alembic migration generated with `alembic revision --autogenerate`
- [ ] Migration script manually reviewed and cleaned up
- [ ] Data migration strategy defined (if production data exists)
- [ ] Migration tested with `alembic upgrade head` on local DB
- [ ] Downgrade tested with `alembic downgrade -1`
- [ ] Migration script includes all indexes

**Files**:
- `backend/alembic/versions/XXX_update_chat_schema_for_tool_calls.py`

**Migration Strategy**:
```python
# If production conversations exist, we need to:
# 1. Create new UUID columns (conversations.id_new, messages.id_new, messages.conversation_id_new)
# 2. Generate UUIDs for existing rows
# 3. Update foreign key references
# 4. Drop old columns, rename new columns
# 5. Add new fields (tool_calls, tool_call_id, name, title)

# For fresh deployment:
# 1. Drop existing conversations and messages tables (if acceptable)
# 2. Recreate with new schema
```

**Command**:
```bash
cd backend
alembic revision --autogenerate -m "update_chat_schema_for_tool_calls"
# Edit migration file to add data migration logic if needed
alembic upgrade head
```

---

### Task 3: Implement FastMCP Server with Task Tools
**Complexity**: Moderate
**Dependencies**: None (can run in parallel with Task 1-2)
**Estimated Time**: 5 hours

**Acceptance Criteria**:
- [ ] `FastMCP()` initialized in global scope
- [ ] `@mcp.tool()` decorator on all 5 tools
- [ ] All tools accept `user_id: str` parameter
- [ ] Tools validate user_id matches JWT claims
- [ ] Tools return dict with task data
- [ ] Error handling for invalid inputs
- [ ] Docstrings follow OpenAI function calling format
- [ ] `get_mcp_tools()` function exports tools for agent

**Files**:
- `backend/app/ai/mcp_server.py` (create or replace)

**Implementation**:
```python
# backend/app/ai/mcp_server.py
from mcp import FastMCP
from typing import Optional, List, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.task import Task
from app.models.user import User

# Initialize FastMCP in global scope (CRITICAL)
mcp = FastMCP("Todo Task Management MCP Server")

@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: str = "MEDIUM",
    due_date: Optional[str] = None
) -> Dict:
    """Add a new task for the user.

    Args:
        user_id: UUID of the user creating the task
        title: Task title (1-200 characters, required)
        description: Optional detailed description
        priority: Task priority - must be LOW, MEDIUM, or HIGH (default: MEDIUM)
        due_date: Optional due date in ISO format (YYYY-MM-DD)

    Returns:
        Created task object with id, title, description, priority, status, created_at
    """
    async with get_session() as session:
        # Validate user exists
        user = await session.get(User, UUID(user_id))
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Validate priority
        if priority not in ["LOW", "MEDIUM", "HIGH"]:
            raise ValueError("Priority must be LOW, MEDIUM, or HIGH")

        # Create task
        task = Task(
            user_id=UUID(user_id),
            title=title,
            description=description,
            priority=priority,
            due_date=datetime.fromisoformat(due_date) if due_date else None,
            status="PENDING"
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat()
        }

@mcp.tool()
async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 20
) -> List[Dict]:
    """List tasks for the user with optional filtering.

    Args:
        user_id: UUID of the user
        status: Filter by status (PENDING or COMPLETED)
        priority: Filter by priority (LOW, MEDIUM, or HIGH)
        limit: Maximum number of tasks to return (default: 20, max: 100)

    Returns:
        List of task objects matching filters
    """
    # Implementation...
    pass

@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> Dict:
    """Mark a task as completed.

    Args:
        user_id: UUID of the user
        task_id: ID of the task to complete

    Returns:
        Updated task object with status=COMPLETED
    """
    # Implementation...
    pass

@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict:
    """Update task fields.

    Args:
        user_id: UUID of the user
        task_id: ID of the task to update
        title: New title (if provided)
        description: New description (if provided)
        priority: New priority (if provided)
        due_date: New due date in ISO format (if provided)

    Returns:
        Updated task object
    """
    # Implementation...
    pass

@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> Dict:
    """Permanently delete a task.

    Args:
        user_id: UUID of the user
        task_id: ID of the task to delete

    Returns:
        Success confirmation with deleted task id
    """
    # Implementation...
    pass

def get_mcp_tools() -> List[Dict]:
    """Get all registered MCP tools for agent initialization.

    Returns:
        List of tool definitions in OpenAI function calling format
    """
    return mcp.list_tools()
```

**Testing**:
```python
# backend/tests/test_mcp_tools.py
import pytest
from app.ai.mcp_server import add_task, list_tasks, complete_task

@pytest.mark.asyncio
async def test_add_task_success(test_user_id):
    result = await add_task(
        user_id=str(test_user_id),
        title="Test task",
        priority="HIGH"
    )
    assert result["title"] == "Test task"
    assert result["priority"] == "HIGH"
    assert "id" in result

@pytest.mark.asyncio
async def test_add_task_invalid_priority(test_user_id):
    with pytest.raises(ValueError, match="Priority must be"):
        await add_task(
            user_id=str(test_user_id),
            title="Test",
            priority="INVALID"
        )
```

---

### Task 4: Implement Stateless AgentRunner
**Complexity**: Complex
**Dependencies**: Task 1, Task 2, Task 3
**Estimated Time**: 8 hours

**Acceptance Criteria**:
- [ ] `AgentRunner` class created
- [ ] `AsyncOpenAI` client configured for Gemini 2.5 Flash
- [ ] `run(user_id, message, conversation_id)` method implemented
- [ ] `_load_message_history()` reconstructs OpenAI messages format from DB
- [ ] Handles tool_calls JSON deserialization
- [ ] `_execute_tools()` calls MCP tools and returns tool response messages
- [ ] Tool execution loop handles multiple tool calls
- [ ] `_save_messages()` persists user, assistant, and tool messages
- [ ] tool_calls JSON serialized correctly
- [ ] Conversation title auto-generated from first message
- [ ] Error handling for Gemini API failures
- [ ] Error handling for tool execution failures

**Files**:
- `backend/app/ai/agent.py` (refactor existing or create new)

**Implementation** (Stateless Pattern):
```python
# backend/app/ai/agent.py
from openai import AsyncOpenAI
from typing import List, Dict, Optional
from uuid import UUID, uuid4
import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation import Conversation
from app.models.message import Message
from app.ai.mcp_server import get_mcp_tools
from app.database import get_session

class AgentRunner:
    """Stateless AI agent using Gemini 2.5 Flash via OpenAI-compatible API."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = "gemini-2.5-flash"
        self.tools = get_mcp_tools()

    async def run(
        self,
        user_id: UUID,
        message: str,
        conversation_id: Optional[UUID] = None
    ) -> Dict:
        """Run agent with stateless architecture.

        1. Get or create conversation
        2. Load message history from DB
        3. Call Gemini API with tools
        4. Execute tool loop if needed
        5. Save messages to DB
        6. Return response

        Args:
            user_id: User UUID from JWT
            message: User's message text
            conversation_id: Existing conversation UUID or None for new

        Returns:
            {
                "conversation_id": "uuid",
                "response": "Assistant's response text"
            }
        """
        async with get_session() as session:
            # Get or create conversation
            if conversation_id:
                conversation = await session.get(Conversation, conversation_id)
                if not conversation or conversation.user_id != user_id:
                    raise ValueError("Conversation not found or access denied")
            else:
                conversation = Conversation(
                    id=uuid4(),
                    user_id=user_id,
                    title="New Conversation"  # Will update after first message
                )
                session.add(conversation)
                await session.commit()

            # Load message history and reconstruct OpenAI format
            messages = await self._load_message_history(session, conversation.id)

            # Add system prompt if first message
            if not messages:
                messages.append({
                    "role": "system",
                    "content": "You are a helpful AI assistant for managing tasks. You can create, list, update, complete, and delete tasks for the user. Always be concise and friendly."
                })

            # Add new user message
            messages.append({"role": "user", "content": message})

            # Call Gemini API with tools
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # Handle tool calls if present
            if assistant_message.tool_calls:
                # Add assistant message with tool_calls to history
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute tools
                tool_messages = await self._execute_tools(
                    assistant_message.tool_calls,
                    user_id
                )
                messages.extend(tool_messages)

                # Get final response after tool execution
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools
                )

                final_message = final_response.choices[0].message

                # Save all messages to DB
                await self._save_messages(
                    session,
                    conversation.id,
                    user_message=message,
                    assistant_message=final_message.content,
                    tool_calls=assistant_message.tool_calls,
                    tool_responses=tool_messages
                )

                # Update conversation title if first message
                if conversation.title == "New Conversation":
                    conversation.title = message[:50] + "..." if len(message) > 50 else message
                    await session.commit()

                return {
                    "conversation_id": str(conversation.id),
                    "response": final_message.content
                }

            # No tool calls - direct response
            await self._save_messages(
                session,
                conversation.id,
                user_message=message,
                assistant_message=assistant_message.content
            )

            # Update title if first message
            if conversation.title == "New Conversation":
                conversation.title = message[:50] + "..." if len(message) > 50 else message
                await session.commit()

            return {
                "conversation_id": str(conversation.id),
                "response": assistant_message.content
            }

    async def _load_message_history(
        self,
        session: AsyncSession,
        conversation_id: UUID
    ) -> List[Dict]:
        """Load conversation history and reconstruct OpenAI format.

        CRITICAL: Reconstruct exact agent state including tool_calls JSON.
        """
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        messages_db = result.scalars().all()

        openai_messages = []
        for msg in messages_db:
            message_dict = {
                "role": msg.role,
                "content": msg.content
            }

            # Add tool_calls if present (for assistant messages)
            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls

            # Add tool response metadata (for tool messages)
            if msg.role == "tool":
                message_dict["tool_call_id"] = msg.tool_call_id
                message_dict["name"] = msg.name

            openai_messages.append(message_dict)

        return openai_messages

    async def _execute_tools(
        self,
        tool_calls: List,
        user_id: UUID
    ) -> List[Dict]:
        """Execute MCP tool calls and return tool response messages.

        Injects user_id into all tool calls for security.
        """
        from app.ai.mcp_server import (
            add_task, list_tasks, complete_task, update_task, delete_task
        )

        tool_map = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "update_task": update_task,
            "delete_task": delete_task
        }

        tool_messages = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Inject user_id for security
            arguments["user_id"] = str(user_id)

            # Execute tool
            try:
                tool_function = tool_map.get(function_name)
                if not tool_function:
                    result = {"error": f"Unknown tool: {function_name}"}
                else:
                    result = await tool_function(**arguments)

                tool_messages.append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id,
                    "name": function_name
                })
            except Exception as e:
                tool_messages.append({
                    "role": "tool",
                    "content": json.dumps({"error": str(e)}),
                    "tool_call_id": tool_call.id,
                    "name": function_name
                })

        return tool_messages

    async def _save_messages(
        self,
        session: AsyncSession,
        conversation_id: UUID,
        user_message: str,
        assistant_message: str,
        tool_calls: Optional[List] = None,
        tool_responses: Optional[List[Dict]] = None
    ):
        """Save user, assistant, and tool messages to DB.

        CRITICAL: Store tool_calls JSON for state reconstruction.
        """
        # Save user message
        session.add(Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role="user",
            content=user_message
        ))

        # Save tool responses if present
        if tool_responses:
            for tool_msg in tool_responses:
                session.add(Message(
                    id=uuid4(),
                    conversation_id=conversation_id,
                    role="tool",
                    content=tool_msg["content"],
                    tool_call_id=tool_msg["tool_call_id"],
                    name=tool_msg["name"]
                ))

        # Save assistant message
        tool_calls_json = None
        if tool_calls:
            tool_calls_json = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in tool_calls
            ]

        session.add(Message(
            id=uuid4(),
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message,
            tool_calls=tool_calls_json
        ))

        await session.commit()
```

**Testing**:
```python
# backend/tests/test_agent.py
import pytest
from app.ai.agent import AgentRunner
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_agent_run_without_tools(test_user_id):
    """Test simple conversation without tool calls."""
    runner = AgentRunner()

    with patch.object(runner.client.chat.completions, 'create') as mock_create:
        mock_create.return_value = AsyncMock(
            choices=[AsyncMock(message=AsyncMock(
                content="Hello! How can I help?",
                tool_calls=None
            ))]
        )

        result = await runner.run(
            user_id=test_user_id,
            message="Hi there"
        )

        assert "conversation_id" in result
        assert result["response"] == "Hello! How can I help?"

@pytest.mark.asyncio
async def test_agent_run_with_tool_calls(test_user_id):
    """Test conversation with tool execution."""
    # Test tool call flow
    pass
```

---

### Task 5: Create Chat API Endpoints
**Complexity**: Moderate
**Dependencies**: Task 4
**Estimated Time**: 4 hours

**Acceptance Criteria**:
- [ ] `POST /api/chat` endpoint implemented
- [ ] JWT authentication on all endpoints
- [ ] Request validation with Pydantic
- [ ] Error handling (400, 401, 403, 404, 500)
- [ ] `GET /api/chat/conversations` with pagination
- [ ] `GET /api/chat/conversations/{id}` returns full history
- [ ] `DELETE /api/chat/conversations/{id}` with cascade delete
- [ ] Router registered in `main.py`
- [ ] OpenAPI docs auto-generated

**Files**:
- `backend/app/api/chat.py`
- `backend/app/main.py` (register router)

**Implementation**:
```python
# backend/app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.ai.agent import AgentRunner
from app.database import get_session

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str

class ConversationSummary(BaseModel):
    id: UUID
    title: str
    created_at: str
    updated_at: str
    message_count: int

class ConversationListResponse(BaseModel):
    conversations: List[ConversationSummary]
    total: int
    limit: int
    offset: int

class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: str

class ConversationDetailResponse(BaseModel):
    id: UUID
    title: str
    messages: List[MessageResponse]

# Endpoints
@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Process chat message with AI agent."""
    try:
        runner = AgentRunner()
        result = await runner.run(
            user_id=current_user.id,
            message=request.message,
            conversation_id=request.conversation_id
        )
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """List user's conversations with pagination."""
    # Get total count
    count_result = await session.execute(
        select(func.count(Conversation.id))
        .where(Conversation.user_id == current_user.id)
    )
    total = count_result.scalar()

    # Get conversations
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(min(limit, 100))
        .offset(offset)
    )
    conversations_db = result.scalars().all()

    # Get message counts
    conversations = []
    for conv in conversations_db:
        msg_count_result = await session.execute(
            select(func.count(Message.id))
            .where(Message.conversation_id == conv.id)
        )
        msg_count = msg_count_result.scalar()

        conversations.append(ConversationSummary(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
            message_count=msg_count
        ))

    return ConversationListResponse(
        conversations=conversations,
        total=total,
        limit=limit,
        offset=offset
    )

@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get conversation history."""
    conversation = await session.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get messages
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages_db = result.scalars().all()

    messages = [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages_db
    ]

    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        messages=messages
    )

@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Delete a conversation."""
    conversation = await session.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    await session.delete(conversation)
    await session.commit()
```

**Register Router**:
```python
# backend/app/main.py
from app.api import chat

app.include_router(chat.router)
```

---

### Task 6: Build Custom React Chat Widget
**Complexity**: Complex
**Dependencies**: None (can run in parallel)
**Estimated Time**: 6 hours

**Acceptance Criteria**:
- [ ] `CustomChatWidget` component created
- [ ] Uses shadcn/ui components (Card, Button, Input, ScrollArea)
- [ ] Uses lucide-react icons (Send, Loader2, MessageSquare)
- [ ] Message display (user vs assistant bubbles)
- [ ] Input field with send button
- [ ] Auto-scroll to latest message
- [ ] Loading state during API calls
- [ ] Error handling and display
- [ ] Keyboard support (Enter to send, Shift+Enter for newline)
- [ ] Conversation persistence across reloads
- [ ] TypeScript typed properly

**Files**:
- `frontend/components/chat/custom-chat-widget.tsx`
- `frontend/lib/api.ts` (extend for chat endpoints)

**Implementation**:
```typescript
// frontend/components/chat/custom-chat-widget.tsx
"use client"

import { useState, useEffect, useRef } from 'react'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Send, Loader2, MessageSquare, Trash2 } from 'lucide-react'
import { apiClient } from '@/lib/api'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export function CustomChatWidget() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Load conversation from localStorage on mount
  useEffect(() => {
    const savedConvId = localStorage.getItem('current_conversation_id')
    if (savedConvId) {
      loadConversation(savedConvId)
    }
  }, [])

  const loadConversation = async (convId: string) => {
    try {
      const conversation = await apiClient.getConversation(convId)
      setMessages(conversation.messages.filter((m: Message) =>
        m.role === 'user' || m.role === 'assistant'
      ))
      setConversationId(convId)
    } catch (err) {
      console.error('Failed to load conversation:', err)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setError(null)
    setIsLoading(true)

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMsg])

    try {
      const response = await apiClient.sendChatMessage(userMessage, conversationId)

      // Update conversation ID
      if (response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id)
        localStorage.setItem('current_conversation_id', response.conversation_id)
      }

      // Replace temp message and add assistant response
      setMessages(prev => [
        ...prev.filter(m => m.id !== tempUserMsg.id),
        {
          id: `user-${Date.now()}`,
          role: 'user',
          content: userMessage,
          created_at: new Date().toISOString()
        },
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.response,
          created_at: new Date().toISOString()
        }
      ])
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send message')
      // Remove optimistic message on error
      setMessages(prev => prev.filter(m => m.id !== tempUserMsg.id))
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const startNewConversation = () => {
    setMessages([])
    setConversationId(null)
    localStorage.removeItem('current_conversation_id')
    setInput('')
    inputRef.current?.focus()
  }

  return (
    <Card className="flex flex-col h-full bg-slate-900/95 backdrop-blur-xl border-white/10 shadow-2xl">
      <CardHeader className="border-b border-white/10 pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-400" />
            <h2 className="text-xl font-semibold text-white">AI Task Assistant</h2>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={startNewConversation}
            className="text-slate-400 hover:text-white"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            New Chat
          </Button>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-0">
        <ScrollArea className="h-full px-4 py-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <MessageSquare className="w-16 h-16 mb-4 opacity-50" />
              <p className="text-lg">Start chatting to manage your tasks</p>
              <p className="text-sm mt-2">Try: "Add a task to buy groceries"</p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                    : 'bg-white/5 border border-white/10 text-slate-100'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-white/5 border border-white/10 rounded-lg px-4 py-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
              </div>
            </div>
          )}

          <div ref={scrollRef} />
        </ScrollArea>
      </CardContent>

      <CardFooter className="border-t border-white/10 pt-4">
        {error && (
          <div className="mb-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded px-3 py-2">
            {error}
          </div>
        )}

        <div className="flex gap-2 w-full">
          <Input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about your tasks..."
            disabled={isLoading}
            className="flex-1 bg-white/5 border-white/10 text-white placeholder:text-slate-400 focus:border-blue-500/50 focus:ring-blue-500/20"
          />
          <Button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}
```

**API Client Extension**:
```typescript
// frontend/lib/api.ts (add to existing apiClient)

async sendChatMessage(message: string, conversationId?: string | null) {
  const response = await this.client.post('/api/chat', {
    message,
    conversation_id: conversationId
  })
  return response.data
}

async getConversations(limit = 20, offset = 0) {
  const response = await this.client.get('/api/chat/conversations', {
    params: { limit, offset }
  })
  return response.data
}

async getConversation(conversationId: string) {
  const response = await this.client.get(`/api/chat/conversations/${conversationId}`)
  return response.data
}

async deleteConversation(conversationId: string) {
  await this.client.delete(`/api/chat/conversations/${conversationId}`)
}
```

---

### Task 7: Create Chat Page with Nebula 2025 Styling
**Complexity**: Moderate
**Dependencies**: Task 6
**Estimated Time**: 3 hours

**Acceptance Criteria**:
- [ ] Chat page created at `frontend/app/chat/page.tsx`
- [ ] Nebula 2025 styling applied (dark theme, glass-morphism)
- [ ] Full-height layout
- [ ] Responsive design (mobile + desktop)
- [ ] Page header with title
- [ ] Widget takes full available height
- [ ] Background gradient effects
- [ ] Added to navigation menu

**Files**:
- `frontend/app/chat/page.tsx`
- `frontend/app/globals.css` (Nebula theme variables)
- `frontend/components/nav.tsx` (add chat link)

**Implementation**:
```typescript
// frontend/app/chat/page.tsx
import { CustomChatWidget } from '@/components/chat/custom-chat-widget'

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Background effects */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none" />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-purple-900/20 via-transparent to-transparent pointer-events-none" />

      <div className="relative container mx-auto h-screen p-4 flex flex-col">
        <header className="mb-6 text-center">
          <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-2">
            AI Task Assistant
          </h1>
          <p className="text-slate-400">
            Chat naturally to manage your tasks
          </p>
        </header>

        <div className="flex-1 min-h-0">
          <CustomChatWidget />
        </div>
      </div>
    </div>
  )
}
```

**Nebula Theme Variables**:
```css
/* frontend/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Nebula 2025 Dark Theme */
    --nebula-bg: 15 23 42; /* slate-950 */
    --nebula-surface: 30 41 59; /* slate-900 */
    --nebula-border: 255 255 255 / 0.1; /* white/10 */
    --nebula-text: 248 250 252; /* slate-50 */
    --nebula-text-muted: 148 163 184; /* slate-400 */
    --nebula-primary: 59 130 246; /* blue-500 */
    --nebula-secondary: 168 85 247; /* purple-500 */
  }
}

@layer utilities {
  .nebula-glass {
    @apply bg-white/5 backdrop-blur-xl border border-white/10;
  }

  .nebula-gradient {
    @apply bg-gradient-to-r from-blue-500 to-purple-500;
  }

  .nebula-glow {
    @apply shadow-lg shadow-blue-500/20;
  }
}
```

---

### Task 8: Integration Testing
**Complexity**: Moderate
**Dependencies**: All previous tasks
**Estimated Time**: 4 hours

**Acceptance Criteria**:
- [ ] End-to-end test: User sends message, receives response
- [ ] Test: User creates task via chat, task appears in dashboard
- [ ] Test: User lists tasks via chat
- [ ] Test: User completes task via chat
- [ ] Test: Conversation persists across page reload
- [ ] Test: Error handling (network failure, invalid input)
- [ ] Test: JWT authentication required
- [ ] Test: User isolation (can't access other users' conversations)

**Files**:
- `backend/tests/test_chat_integration.py`
- `frontend/__tests__/chat.test.tsx` (if using Jest/React Testing Library)

**Backend Integration Test**:
```python
# backend/tests/test_chat_integration.py
import pytest
from httpx import AsyncClient
from app.main import app
from app.models.user import User

@pytest.mark.asyncio
async def test_chat_end_to_end(test_client: AsyncClient, test_user_token: str):
    """Test complete chat flow from message to task creation."""

    # Send message to create task
    response = await test_client.post(
        "/api/chat",
        json={"message": "Add a task to buy groceries with high priority"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "response" in data
    conversation_id = data["conversation_id"]

    # Verify conversation exists
    response = await test_client.get(
        f"/api/chat/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    conversation = response.json()
    assert len(conversation["messages"]) >= 2  # User + assistant

    # Verify task was created in dashboard
    response = await test_client.get(
        "/api/tasks",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    tasks = response.json()
    assert any("groceries" in task["title"].lower() for task in tasks)

@pytest.mark.asyncio
async def test_chat_user_isolation(
    test_client: AsyncClient,
    test_user_token: str,
    other_user_token: str
):
    """Test that users cannot access other users' conversations."""

    # User 1 creates conversation
    response = await test_client.post(
        "/api/chat",
        json={"message": "Hello"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    conversation_id = response.json()["conversation_id"]

    # User 2 tries to access User 1's conversation
    response = await test_client.get(
        f"/api/chat/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {other_user_token}"}
    )
    assert response.status_code == 403
```

---

## Testing Strategy

### Unit Tests

**Backend**:
1. **MCP Tools** (`tests/test_mcp_tools.py`):
   - Test each tool with valid inputs
   - Test validation errors (invalid priority, missing user_id)
   - Test user isolation (tool rejects wrong user_id)

2. **AgentRunner** (`tests/test_agent.py`):
   - Test message history reconstruction
   - Test tool execution loop
   - Test message saving with tool_calls JSON
   - Mock Gemini API responses

3. **Chat API** (`tests/test_chat_api.py`):
   - Test endpoint authentication
   - Test request validation
   - Test conversation CRUD operations

**Frontend**:
1. **CustomChatWidget** (`__tests__/chat-widget.test.tsx`):
   - Test message rendering
   - Test input handling
   - Test API integration (mocked)
   - Test loading states

### Integration Tests

1. **Full Chat Flow**:
   - User sends message → Agent responds → Tool executed → Task created
2. **Conversation Persistence**:
   - Create conversation → Reload page → History restored
3. **Error Scenarios**:
   - Network failure → Error displayed
   - Invalid tool arguments → Error message returned by agent

### End-to-End Tests (Optional)

Using Playwright:
1. Login → Navigate to chat → Send message → Verify response
2. Create task via chat → Navigate to dashboard → Verify task exists
3. List tasks via chat → Verify correct tasks shown

---

## Risks & Mitigations

### Risk 1: UUID Migration Breaks Existing Data
**Probability**: High (if production conversations exist)
**Impact**: Critical
**Mitigation**:
- Create comprehensive data migration script
- Test migration on copy of production DB first
- Have rollback plan (restore from backup)
- Consider soft launch (new chat feature, preserve old if exists)

### Risk 2: Gemini API Rate Limits or Failures
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Implement retry logic with exponential backoff
- Add API key rotation if hitting limits
- Implement circuit breaker pattern
- Show user-friendly error messages
- Log all API failures for monitoring

### Risk 3: tool_calls JSON Reconstruction Complexity
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Write comprehensive unit tests for reconstruction logic
- Test with multiple tool call scenarios
- Validate JSON format matches OpenAI spec exactly
- Add logging for debugging state reconstruction issues

### Risk 4: Frontend-Backend Type Mismatches
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Use api-schema-sync skill to validate types
- Add integration tests that catch type errors
- Generate TypeScript types from Pydantic models (optional)

### Risk 5: Performance Issues with Long Conversations
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Limit message history to 50 recent messages
- Implement pagination for conversation list
- Add database indexes on query fields
- Monitor query performance

---

## Dependencies

**External**:
- Google Gemini API (via OpenAI-compatible endpoint)
- Neon PostgreSQL database

**Internal**:
- User authentication system (JWT)
- Existing task CRUD operations
- Database connection pool

**Blocking**:
- None (all dependencies already met)

**Optional**:
- Streaming support (defer to future iteration)

---

## Success Metrics

**Functional**:
- [ ] All 10 acceptance criteria from spec met
- [ ] All unit tests passing (80%+ coverage)
- [ ] All integration tests passing
- [ ] Manual E2E test successful

**Non-Functional**:
- [ ] Chat response time < 3s (p95)
- [ ] Frontend loads in < 1s
- [ ] No React ChatKit dependencies in package.json
- [ ] No security vulnerabilities (JWT enforced, user isolation)
- [ ] Gemini API errors handled gracefully

**User Experience**:
- [ ] User can create task via chat in natural language
- [ ] User can list tasks via chat
- [ ] User can complete/update/delete tasks via chat
- [ ] Conversation history persists across sessions
- [ ] UI feels premium (Nebula styling)

---

## Rollback Plan

If critical bugs found after deployment:

### Backend Rollback:
1. **Database**: `alembic downgrade -1` (if migration applied)
2. **Code**: `git revert <commit>` and redeploy
3. **Data**: Restore from backup if data corrupted

### Frontend Rollback:
1. **Vercel**: Revert to previous deployment
2. **Code**: `git revert <commit>` and redeploy

### Safe Rollback Window:
- 48 hours after deployment (before users create significant chat history)

---

## Post-Implementation

After completing all tasks:

1. **Staging Deployment**:
   - Deploy backend to staging environment
   - Deploy frontend to Vercel preview
   - Test with real Gemini API key
   - Verify conversation persistence

2. **User Acceptance Testing**:
   - Invite beta users to test chat feature
   - Gather feedback on UX
   - Identify edge cases

3. **Performance Testing**:
   - Load test with 100 concurrent users
   - Monitor Gemini API latency
   - Check database query performance

4. **Documentation**:
   - Update API docs with chat endpoints
   - Create user guide for chat feature
   - Document MCP tool development process

5. **Create PHR**:
   - Document implementation process
   - Record architectural decisions
   - Note challenges and solutions

6. **Production Deployment**:
   - Deploy backend to production
   - Run database migration
   - Deploy frontend to production
   - Monitor error rates and performance

7. **Monitoring**:
   - Set up alerts for Gemini API failures
   - Monitor chat usage metrics
   - Track conversation creation rate
   - Monitor database growth

---

## Future Enhancements (Out of Scope)

**Phase III+**:
- Streaming responses (Server-Sent Events)
- Conversation search functionality
- Export conversation to PDF/Markdown
- Voice input/output
- Image/file uploads in chat
- Multi-turn context window optimization
- Custom AI personality configuration

**Phase IV** (Microservices):
- Separate chat service
- Dedicated agent orchestration service
- Async tool execution with job queue

**Phase V** (Event-Driven):
- Broadcast task changes to chat via events
- Real-time typing indicators
- Multi-user conversations (collaboration)

---

## Appendix: Key Code Patterns

### Pattern 1: Stateless Agent Reconstruction

```python
# Load history from DB
messages_db = session.query(Message).filter(
    Message.conversation_id == conversation_id
).order_by(Message.created_at.asc()).all()

# Reconstruct OpenAI format
openai_messages = []
for msg in messages_db:
    message_dict = {"role": msg.role, "content": msg.content}

    # Add tool_calls if present (stored as JSON)
    if msg.tool_calls:
        message_dict["tool_calls"] = msg.tool_calls  # Already deserialized by SQLAlchemy JSON type

    # Add tool response metadata
    if msg.role == "tool":
        message_dict["tool_call_id"] = msg.tool_call_id
        message_dict["name"] = msg.name

    openai_messages.append(message_dict)
```

### Pattern 2: FastMCP Global Initialization

```python
# MUST be at module level (global scope)
from mcp import FastMCP

mcp = FastMCP("Server Name")

@mcp.tool()
async def my_tool(arg1: str, arg2: int) -> dict:
    """Tool description for LLM."""
    return {"result": "value"}

# Export for agent
def get_tools():
    return mcp.list_tools()
```

### Pattern 3: Tool Execution with user_id Injection

```python
# Security: Always inject user_id from JWT, never trust client input
tool_calls = response.choices[0].message.tool_calls

for tool_call in tool_calls:
    arguments = json.loads(tool_call.function.arguments)
    arguments["user_id"] = str(current_user.id)  # Inject from JWT

    result = await execute_tool(tool_call.function.name, **arguments)
```

### Pattern 4: Nebula 2025 Glass Morphism

```typescript
// Component with glass effect
<div className="bg-slate-900/95 backdrop-blur-xl border border-white/10 shadow-2xl">
  {/* Content */}
</div>

// Gradient button
<button className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 shadow-lg shadow-blue-500/20">
  Send
</button>

// User message bubble
<div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20 rounded-lg px-4 py-2">
  {message}
</div>

// Assistant message bubble
<div className="bg-white/5 border border-white/10 text-slate-100 rounded-lg px-4 py-2">
  {message}
</div>
```

---

## Quality Checklist

Before marking plan complete:
- [x] Spec fully read and understood
- [x] Architecture aligns with Phase III constraints
- [x] Database schema includes tool_calls JSON field
- [x] FastMCP pattern documented
- [x] Stateless agent pattern explained
- [x] All tasks have clear acceptance criteria
- [x] Task dependencies identified
- [x] Testing strategy covers unit + integration + E2E
- [x] Risks identified with mitigations
- [x] Success metrics defined
- [x] Rollback plan documented
- [x] NO React ChatKit dependencies specified
- [x] Nebula 2025 styling detailed

---

**Plan Status**: ✅ Ready for Implementation

**Next Steps**:
1. Review plan with user
2. Get approval
3. Begin Task 1 (Database schema updates)
4. Track progress with TodoWrite tool
5. Update plan if challenges discovered during implementation
