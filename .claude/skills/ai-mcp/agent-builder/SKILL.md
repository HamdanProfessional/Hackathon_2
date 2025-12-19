---
name: agent-builder
description: Build AI agents using AsyncOpenAI with Google Gemini for task management chatbots. Use when Claude needs to create stateless AI agents that integrate with MCP tools for CRUD operations, manage conversation persistence, and understand natural language commands for todo management.
license: Complete terms in LICENSE.txt
---

# Agent Builder

Builds stateless AI agents with Gemini integration and MCP tool support.

## Quick Start

Create AI agent:
```bash
/skill agent-builder
```

## Implementation

### 1. Initialize Agent Service
Create `backend/app/ai/agent.py`:
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

### 2. Add MCP Tools
Integrate tools in `backend/app/ai/tools.py`:
- `add_task` - Create new tasks
- `list_tasks` - Retrieve and filter
- `complete_task` - Mark as complete
- `update_task` - Modify details
- `delete_task` - Remove with confirmation

### 3. Implement Chat Endpoint
Create `backend/app/api/chat.py`:
- JWT authentication
- Rate limiting (10 req/min)
- Conversation persistence
- Tool execution loop

### 4. Frontend Integration
Add React chat component:
- Markdown rendering
- Loading indicators
- Message persistence
- Responsive design

## Key Features

### Natural Language Processing
- Task creation: "Add buy milk to my todos"
- Completion: "I finished the report"
- Updates: "Change meeting to tomorrow"
- Queries: "Show me high priority tasks"

### Safety Protocols
- Confirmation for destructive operations
- Fuzzy matching for task identification
- Error handling for API failures
- Rate limiting per user

## Architecture

```
User Request → FastAPI Endpoint → Agent Service → Gemini API
                                    ↓
                              MCP Tools → PostgreSQL
                                    ↓
                              Response → Frontend
```

## Configuration

Environment variables:
```bash
GEMINI_API_KEY=your-key-here
AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
AI_MODEL=gemini-2.5-flash
```

## Testing

Verify:
- Natural language commands work
- All CRUD operations functional
- Conversation persists across sessions
- Error handling graceful
- Rate limiting active