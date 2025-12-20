# Feature: Phase III - AI Chatbot (Python Agent Architecture)

## Overview
Implement a conversational AI assistant for task management using Python-based agent architecture with Gemini 2.5 Flash. The system uses `openai-agents` SDK for orchestration, `mcp` SDK with FastMCP pattern for tools, and a custom React chat widget. This is a complete re-implementation that eliminates all React ChatKit dependencies and establishes Python as the core chat engine.

## User Stories
- **US-1**: As a user, I want to chat naturally with an AI assistant to manage my tasks, so that I can avoid using traditional forms and buttons
- **US-2**: As a user, I want the AI to remember our conversation history, so that I can refer to previous context without repeating myself
- **US-3**: As a user, I want the AI to execute task operations (add, list, complete, update, delete) on my behalf, so that task management feels conversational
- **US-4**: As a user, I want a modern, glass-morphism styled chat interface, so that the experience feels premium and engaging
- **US-5**: As a user, I want the chat to work seamlessly with my existing tasks, so that there's no friction between chat and dashboard views

## Acceptance Criteria
- [ ] **AC-1**: Backend uses `openai>=1.0` with Gemini 2.5 Flash model via AsyncOpenAI
- [ ] **AC-2**: Backend uses `mcp` SDK with FastMCP pattern for tool registration
- [ ] **AC-3**: All MCP tools accept `user_id` parameter for multi-tenant isolation
- [ ] **AC-4**: Agent architecture is stateless - conversation history loaded from Neon DB on each request
- [ ] **AC-5**: Messages table stores `tool_calls` JSON field for agent state reconstruction
- [ ] **AC-6**: Frontend uses custom React component built with shadcn/ui and lucide-react (NO @openai/chatkit-react)
- [ ] **AC-7**: API endpoint `/api/chat` supports POST with streaming responses
- [ ] **AC-8**: Frontend applies Nebula 2025 styling (dark theme with glass-morphism effects)
- [ ] **AC-9**: User can create, list, complete, update, and delete tasks via natural language
- [ ] **AC-10**: Conversation history persists across page reloads

## Architecture Constraints

### Critical Rules
1. **NO React ChatKit**: Frontend must be a custom component
2. **Python is Core**: All agent logic, tool execution, and state management in Python
3. **Stateless Design**: Agent must reconstruct state from database on every request
4. **FastMCP Pattern**: Use `FastMCP()` for tool registration (not manual SDK calls)
5. **Gemini 2.5 Flash**: Model must be `gemini-2.5-flash` via OpenAI-compatible endpoint

### Technology Stack
- **Backend AI Engine**:
  - `openai>=1.0` (AsyncOpenAI client)
  - `openai-agents` SDK for agent orchestration
  - `mcp` SDK with FastMCP for tool definitions
- **Backend API**: FastAPI with async/await
- **Database**: Neon PostgreSQL via SQLModel
- **Frontend**: Next.js 14 + TypeScript + shadcn/ui + lucide-react
- **Styling**: Tailwind CSS with Nebula 2025 theme (dark/glass-morphism)

## Data Model (Backend)

### 1. Conversations Table
**Model**: `Conversation`
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to User, indexed)
- `title`: String(200) - Generated from first message or "New Conversation"
- `created_at`: DateTime (UTC, auto)
- `updated_at`: DateTime (UTC, auto)

**Relationships**:
- `user`: Many-to-One with User
- `messages`: One-to-Many with Message

**Indexes**:
- `user_id` for fast user-specific queries
- `created_at DESC` for recent conversations

### 2. Messages Table
**Model**: `Message`
- `id`: UUID (Primary Key)
- `conversation_id`: UUID (Foreign Key to Conversation, indexed)
- `role`: Enum['user', 'assistant', 'system'] (indexed)
- `content`: Text - The message text
- `tool_calls`: JSON (nullable) - Stores OpenAI tool_calls format for agent state reconstruction
- `tool_call_id`: String(100, nullable) - OpenAI tool call identifier
- `name`: String(100, nullable) - Tool name if role='tool'
- `created_at`: DateTime (UTC, auto)

**Relationships**:
- `conversation`: Many-to-One with Conversation

**Indexes**:
- `conversation_id, created_at ASC` for chronological message retrieval
- `role` for filtering assistant/user messages

**Critical Field**: `tool_calls`
- Stores JSON array of tool call objects
- Format matches OpenAI API: `[{"id": "call_xyz", "type": "function", "function": {"name": "add_task", "arguments": "{...}"}}]`
- Enables stateless agent to reconstruct exact execution state
- Example:
  ```json
  [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "add_task",
        "arguments": "{\"user_id\": \"uuid\", \"title\": \"Buy groceries\", \"priority\": \"MEDIUM\"}"
      }
    }
  ]
  ```

## API Endpoints

### 1. Create/Continue Conversation
- **Method**: POST
- **Path**: `/api/chat`
- **Auth**: Required (JWT Bearer token)
- **Request Body**:
  ```json
  {
    "message": "Add a task to buy groceries",
    "conversation_id": "uuid-optional"
  }
  ```
- **Response (200 - Streaming)**:
  - Content-Type: `text/event-stream`
  - Streams assistant response chunks in real-time
  - Final event includes `conversation_id`
- **Response (200 - Non-Streaming)**:
  ```json
  {
    "conversation_id": "uuid",
    "response": "I've added 'Buy groceries' to your tasks with medium priority.",
    "tool_calls": [
      {
        "tool": "add_task",
        "arguments": {"title": "Buy groceries", "priority": "MEDIUM"},
        "result": {"id": 123, "title": "Buy groceries"}
      }
    ]
  }
  ```
- **Errors**:
  - `400`: Invalid message format
  - `401`: Unauthorized (missing/invalid JWT)
  - `404`: Conversation not found or not owned by user
  - `500`: Agent execution error

### 2. List Conversations
- **Method**: GET
- **Path**: `/api/chat/conversations`
- **Auth**: Required
- **Query Params**:
  - `limit`: Integer (default: 20, max: 100)
  - `offset`: Integer (default: 0)
- **Response (200)**:
  ```json
  {
    "conversations": [
      {
        "id": "uuid",
        "title": "Task Management Discussion",
        "created_at": "2025-01-15T10:30:00Z",
        "updated_at": "2025-01-15T11:45:00Z",
        "message_count": 12
      }
    ],
    "total": 45,
    "limit": 20,
    "offset": 0
  }
  ```

### 3. Get Conversation History
- **Method**: GET
- **Path**: `/api/chat/conversations/{conversation_id}`
- **Auth**: Required
- **Response (200)**:
  ```json
  {
    "id": "uuid",
    "title": "Task Management Discussion",
    "messages": [
      {
        "id": "uuid",
        "role": "user",
        "content": "Show me my high priority tasks",
        "created_at": "2025-01-15T10:30:00Z"
      },
      {
        "id": "uuid",
        "role": "assistant",
        "content": "Here are your high priority tasks:\n1. Submit report by Friday\n2. Call client",
        "tool_calls": [...],
        "created_at": "2025-01-15T10:30:05Z"
      }
    ]
  }
  ```
- **Errors**:
  - `401`: Unauthorized
  - `403`: Forbidden (conversation not owned by user)
  - `404`: Conversation not found

### 4. Delete Conversation
- **Method**: DELETE
- **Path**: `/api/chat/conversations/{conversation_id}`
- **Auth**: Required
- **Response (204)**: No content
- **Errors**:
  - `401`: Unauthorized
  - `403`: Forbidden
  - `404`: Not found

## Backend Implementation

### 1. FastMCP Server (`backend/app/ai/mcp_server.py`)
```python
from mcp import FastMCP
from typing import Optional
from uuid import UUID

# Initialize FastMCP in global scope
mcp = FastMCP("Todo Assistant MCP Server")

@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: str = "MEDIUM",
    due_date: Optional[str] = None
) -> dict:
    """Add a new task for the user.

    Args:
        user_id: UUID of the user creating the task
        title: Task title (1-200 chars)
        description: Optional task description
        priority: Task priority (LOW, MEDIUM, HIGH)
        due_date: Optional due date (ISO format)

    Returns:
        Created task object with id, title, priority, etc.
    """
    # Implementation calls backend/app/crud/tasks.py
    pass

@mcp.tool()
async def list_tasks(
    user_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 20
) -> list[dict]:
    """List tasks for the user with optional filtering.

    Args:
        user_id: UUID of the user
        status: Filter by status (PENDING, COMPLETED)
        priority: Filter by priority (LOW, MEDIUM, HIGH)
        limit: Maximum number of tasks to return

    Returns:
        List of task objects
    """
    pass

@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as completed.

    Args:
        user_id: UUID of the user
        task_id: ID of the task to complete

    Returns:
        Updated task object
    """
    pass

@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None
) -> dict:
    """Update task fields.

    Args:
        user_id: UUID of the user
        task_id: ID of the task to update
        title: New title (if provided)
        description: New description (if provided)
        priority: New priority (if provided)
        due_date: New due date (if provided)

    Returns:
        Updated task object
    """
    pass

@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """Permanently delete a task.

    Args:
        user_id: UUID of the user
        task_id: ID of the task to delete

    Returns:
        Success confirmation with deleted task id
    """
    pass

# Export tools for agent
def get_mcp_tools():
    """Get all registered MCP tools for agent initialization."""
    return mcp.list_tools()
```

### 2. Agent Runner (`backend/app/ai/agent.py`)
```python
from openai import AsyncOpenAI
from typing import List, Dict, Optional
import os
from uuid import UUID
from .mcp_server import get_mcp_tools
from ..models.chat import Conversation, Message
from ..db import get_session

class AgentRunner:
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

        1. Load conversation history from DB (if conversation_id provided)
        2. Reconstruct agent state from stored tool_calls
        3. Execute agent with new user message
        4. Save new messages (user, assistant, tool responses) to DB
        5. Return response
        """
        # Get or create conversation
        conversation = await self._get_or_create_conversation(
            user_id, conversation_id
        )

        # Load message history and reconstruct OpenAI format
        messages = await self._load_message_history(conversation.id)

        # Add new user message
        messages.append({"role": "user", "content": message})

        # Call OpenAI API with tools
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )

        # Handle tool calls if present
        if response.choices[0].message.tool_calls:
            # Execute tools and continue conversation
            tool_messages = await self._execute_tools(
                response.choices[0].message.tool_calls,
                user_id
            )
            messages.extend(tool_messages)

            # Get final response after tool execution
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools
            )

            # Save all messages to DB
            await self._save_messages(
                conversation.id,
                message,
                final_response.choices[0].message.content,
                response.choices[0].message.tool_calls
            )

            return {
                "conversation_id": str(conversation.id),
                "response": final_response.choices[0].message.content
            }

        # No tool calls - direct response
        await self._save_messages(
            conversation.id,
            message,
            response.choices[0].message.content
        )

        return {
            "conversation_id": str(conversation.id),
            "response": response.choices[0].message.content
        }

    async def _load_message_history(
        self, conversation_id: UUID
    ) -> List[Dict]:
        """Load and reconstruct OpenAI message format from DB.

        Reconstructs exact agent state including tool_calls.
        """
        # Query messages ordered by created_at
        # Convert to OpenAI format: [{role, content, tool_calls}, ...]
        pass

    async def _execute_tools(
        self, tool_calls: List, user_id: UUID
    ) -> List[Dict]:
        """Execute MCP tool calls and return tool response messages."""
        pass

    async def _save_messages(
        self,
        conversation_id: UUID,
        user_message: str,
        assistant_message: str,
        tool_calls: Optional[List] = None
    ):
        """Save user and assistant messages to DB.

        Stores tool_calls JSON for state reconstruction.
        """
        pass
```

### 3. Chat API Endpoint (`backend/app/api/chat.py`)
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from ..ai.agent import AgentRunner
from ..auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user = Depends(get_current_user)
):
    """Process chat message with AI agent."""
    runner = AgentRunner()
    result = await runner.run(
        user_id=current_user.id,
        message=request.message,
        conversation_id=request.conversation_id
    )
    return result

@router.get("/conversations")
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """List user's conversations."""
    pass

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    current_user = Depends(get_current_user)
):
    """Get conversation history."""
    pass

@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    current_user = Depends(get_current_user)
):
    """Delete a conversation."""
    pass
```

## Frontend Implementation

### 1. Custom Chat Widget (`frontend/components/chat/custom-chat-widget.tsx`)
**Requirements**:
- Built with shadcn/ui components (Card, Button, Input, ScrollArea)
- Uses lucide-react icons (Send, Loader2, MessageSquare)
- Nebula 2025 styling (dark theme, glass-morphism, gradient accents)
- Real-time message rendering
- Loading states during API calls
- Auto-scroll to latest message
- Keyboard support (Enter to send, Shift+Enter for newline)

**Component Structure**:
```typescript
"use client"

import { useState, useEffect, useRef } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Send, Loader2, MessageSquare } from 'lucide-react'
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
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  // Handle send message
  // Load conversation history
  // Render messages with Nebula styling
}
```

**Styling (Nebula 2025)**:
- Background: `bg-slate-900/95 backdrop-blur-xl`
- Glass effect: `border border-white/10 shadow-2xl`
- Message bubbles:
  - User: `bg-gradient-to-r from-blue-600 to-purple-600 text-white`
  - Assistant: `bg-white/5 border border-white/10 text-slate-100`
- Input: `bg-white/5 border-white/10 text-white placeholder:text-slate-400`
- Button: `bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600`
- Glow effects: `shadow-lg shadow-blue-500/20`

### 2. Chat Page (`frontend/app/chat/page.tsx`)
```typescript
import { CustomChatWidget } from '@/components/chat/custom-chat-widget'

export default function ChatPage() {
  return (
    <div className="container mx-auto h-screen p-4">
      <div className="flex flex-col h-full">
        <header className="mb-4">
          <h1 className="text-3xl font-bold text-white">AI Task Assistant</h1>
          <p className="text-slate-400">Chat naturally to manage your tasks</p>
        </header>
        <div className="flex-1 min-h-0">
          <CustomChatWidget />
        </div>
      </div>
    </div>
  )
}
```

### 3. API Client Extension (`frontend/lib/api.ts`)
```typescript
// Add to existing apiClient
async sendChatMessage(message: string, conversationId?: string) {
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

## Dependencies

### Backend (requirements.txt)
```
# Existing dependencies
fastapi>=0.104.0
sqlmodel>=0.0.14
alembic>=1.12.0
psycopg2-binary>=2.9.9
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
uvicorn[standard]>=0.24.0

# NEW for Phase III
openai>=1.0.0           # AsyncOpenAI client for Gemini
mcp>=0.1.0              # Official MCP SDK
```

### Frontend (package.json - NO CHANGES)
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "typescript": "^5.3.3",
    "@radix-ui/react-*": "latest",
    "lucide-react": "^0.294.0",
    "tailwindcss": "^3.4.0",
    "axios": "^1.6.0"
  }
}
```

**Critical**: Do NOT add `@openai/chatkit-react` or any ChatKit React dependencies.

## Database Migrations

### Migration: Add Conversations and Messages Tables
```python
# backend/alembic/versions/XXX_add_chat_tables.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

def upgrade():
    # Conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('title', sa.String(200), nullable=False, default='New Conversation'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='message_role'), nullable=False, index=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('tool_calls', JSON, nullable=True),  # CRITICAL: Store OpenAI tool_calls format
        sa.Column('tool_call_id', sa.String(100), nullable=True),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    # Index for chronological retrieval
    op.create_index(
        'idx_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at']
    )

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

## Integration Points

### 1. Task Dashboard Integration
- Add "Ask AI" floating button to dashboard
- Opens chat widget in sidebar/modal
- User can switch between dashboard and chat views seamlessly

### 2. Authentication
- Chat endpoints require JWT authentication (existing auth system)
- All MCP tools receive `user_id` from JWT claims
- Conversation ownership enforced via `user_id` FK

### 3. Multi-Tenancy
- All database queries filter by `user_id`
- Agent cannot access other users' tasks
- Conversation isolation per user

## Non-Functional Requirements

### Performance
- **API Response Time**: <2s for simple queries, <5s for complex tool executions
- **Database Queries**: Indexed on `user_id`, `conversation_id`, `created_at`
- **Message History**: Load max 50 recent messages per conversation
- **Connection Pooling**: Reuse database connections via SQLModel session

### Security
- **Authentication**: JWT required for all chat endpoints
- **Authorization**: Verify user owns conversation before access
- **Input Validation**: Pydantic models validate all requests
- **SQL Injection**: SQLModel ORM prevents injection attacks
- **Tool Security**: All MCP tools validate `user_id` matches JWT claims

### Scalability
- **Stateless Design**: No in-memory state - supports horizontal scaling
- **Database**: Neon PostgreSQL handles concurrent users
- **Tool Execution**: Async/await prevents blocking

### Accessibility
- **Keyboard Navigation**: Full keyboard support in chat widget
- **Screen Readers**: Semantic HTML with ARIA labels
- **Focus Management**: Proper focus trap in chat input

### Testing
- **Unit Tests**: Test agent runner, MCP tools, message reconstruction
- **Integration Tests**: Test full chat flow from API to database
- **E2E Tests**: Playwright tests for chat widget interactions
- **Tool Tests**: Verify each MCP tool with valid/invalid inputs

## Implementation Phases

### Phase 1: Backend Foundation (Days 1-2)
1. Install dependencies (`openai`, `mcp`)
2. Create database models (`Conversation`, `Message`)
3. Run Alembic migrations
4. Implement FastMCP server with 5 tools
5. Test tools in isolation

### Phase 2: Agent Integration (Days 3-4)
1. Implement `AgentRunner` class
2. Configure Gemini 2.5 Flash connection
3. Implement stateless message reconstruction
4. Test agent with sample conversations
5. Verify tool execution loop

### Phase 3: API Endpoints (Day 5)
1. Create `/api/chat` POST endpoint
2. Create conversation list/get/delete endpoints
3. Implement error handling
4. Add request validation
5. Test API with Postman/curl

### Phase 4: Frontend Widget (Days 6-7)
1. Create `CustomChatWidget` component
2. Implement message rendering
3. Add input handling and API calls
4. Apply Nebula 2025 styling
5. Test chat interactions

### Phase 5: Integration & Polish (Day 8)
1. Integrate chat into main app navigation
2. Add conversation history sidebar
3. Implement loading states and error handling
4. Test end-to-end flow
5. Fix bugs and polish UX

### Phase 6: Testing & Validation (Day 9)
1. Write unit tests for tools and agent
2. Write integration tests for API
3. Write E2E tests for chat widget
4. Perform manual testing
5. Validate against acceptance criteria

## Out of Scope
- Voice input/output
- Image/file uploads in chat
- Multi-user conversations (collaboration)
- Real-time typing indicators
- Message reactions/threading
- Advanced AI personality configuration
- Integration with external AI services beyond Gemini
- Export chat history to PDF/CSV
- Search within conversations

## Validation Checklist

### Backend
- [ ] `openai` and `mcp` installed in requirements.txt
- [ ] Gemini API key configured in environment
- [ ] FastMCP server with 5 tools (`add_task`, `list_tasks`, `complete_task`, `update_task`, `delete_task`)
- [ ] All tools accept `user_id` parameter
- [ ] `AgentRunner` loads conversation history from DB
- [ ] `tool_calls` JSON field stored in messages table
- [ ] `/api/chat` endpoint returns valid responses
- [ ] Conversation CRUD endpoints work correctly

### Frontend
- [ ] NO `@openai/chatkit-react` in package.json
- [ ] `CustomChatWidget` component exists
- [ ] Widget uses shadcn/ui components
- [ ] Nebula 2025 styling applied (dark/glass)
- [ ] Messages render correctly (user vs assistant)
- [ ] Input sends message to `/api/chat`
- [ ] Loading states displayed during API calls
- [ ] Conversation history persists across reloads

### Integration
- [ ] User can login and access chat
- [ ] Chat creates tasks visible in dashboard
- [ ] Chat lists tasks from database
- [ ] Chat completes tasks
- [ ] Chat updates task properties
- [ ] Chat deletes tasks
- [ ] All operations respect user isolation

## Success Metrics
- User can complete 5 task operations via chat in <2 minutes
- Chat responds to queries in <3 seconds average
- Zero unauthorized access to other users' conversations
- 95% tool execution success rate
- Frontend loads in <1 second
- No React ChatKit dependencies remain

## References
- OpenAI Python SDK: https://github.com/openai/openai-python
- MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- FastMCP Documentation: [Internal MCP docs]
- Gemini API (OpenAI compatible): https://ai.google.dev/gemini-api/docs/openai
- shadcn/ui Components: https://ui.shadcn.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Next.js 14 App Router: https://nextjs.org/docs/app
