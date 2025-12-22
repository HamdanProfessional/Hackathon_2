# AI Chatbot Builder Skill

Build stateless AI chatbot with MCP tools and database persistence.

## When to Use This Skill

Use this skill when you need to:
- Add AI chatbot interface to your application
- Create MCP (Model Context Protocol) tools for AI agents
- Implement stateless conversation management with database persistence
- Set up Groq/OpenAI/Gemini AI providers with fallback

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `tools` | array | Yes | MCP tool definitions |
| `ai_provider` | string | No | Primary AI provider (groq, openai, gemini) |
| `enable_voice` | boolean | No | Enable speech recognition/synthesis |

## MCP Tool Definition

```json
{
  "name": "add_task",
  "description": "Create a new task",
  "parameters": {
    "title": {"type": "string", "required": true},
    "description": {"type": "string", "required": false}
  }
}
```

## Generated Architecture

```
┌─────────────┐     ┌──────────────────────────────────┐
│   Frontend  │────▶│       FastAPI Backend          │
│  (Next.js)  │     │  ┌────────────────────────────┐ │
│             │     │  │    POST /api/chat          │ │
│             │     │  └──────────┬─────────────────┘ │
│             │     │             │                   │
│             │     │             ▼                   │
│             │     │  ┌────────────────────────────┐ │
│             │     │  │  AI Agent (Groq/OpenAI)    │ │
│             │     │  └──────────┬─────────────────┘ │
│             │     │             │                   │
│             │     │             ▼                   │
│             │     │  ┌────────────────────────────┐ │
│             │     │  │       MCP Tools           │ │
│             │     │  │  - add_task               │ │
│             │     │  │  - list_tasks              │ │
│             │     │  │  - complete_task           │ │
│             │     │  └──────────┬─────────────────┘ │
└─────────────┘     └─────────────┼───────────────────┘
                                  │
                                  ▼
                           ┌──────────────┐
                           │   Neon DB    │
                           │              │
                           │ - tasks      │
                           │ - messages   │
                           │ - conversations│
                           └──────────────┘
```

## Stateless Architecture

The chatbot follows a **stateless** architecture:
1. Each request includes `conversation_id` (optional)
2. Conversation history is loaded from database
3. AI agent processes with full context
4. New messages are saved to database
5. No in-memory state (scalable, restart-safe)

## Database Schema

### conversations table
```sql
id              UUID PRIMARY KEY
user_id         UUID NOT NULL
created_at      TIMESTAMP DEFAULT NOW()
updated_at      TIMESTAMP DEFAULT NOW()
```

### messages table
```sql
id              UUID PRIMARY KEY
conversation_id UUID REFERENCES conversations(id)
role            VARCHAR(20) NOT NULL  -- 'user' or 'assistant'
content         TEXT NOT NULL
created_at      TIMESTAMP DEFAULT NOW()
```

## Example Usage

```
@skill ai-chatbot-builder
tools:
  - name: add_task
    description: Create a new todo task
    parameters:
      - name: title
        type: string
        required: true
      - name: description
        type: string
        required: false
  - name: list_tasks
    description: List all user tasks
    parameters:
      - name: status
        type: string
        required: false
ai_provider: groq
enable_voice: true
```

## Generated Components

### Backend
- `backend/app/ai/agent.py` - Stateless AI agent
- `backend/app/ai/mcp_tools.py` - MCP tool implementations
- `backend/app/api/chat.py` - Chat endpoint
- Database migrations for conversations/messages

### Frontend
- `frontend/components/chat/chat-interface.tsx` - Chat UI
- `frontend/lib/chat-client.ts` - API client
- Voice input/output hooks
- Message persistence

## Configuration

### Environment Variables
```bash
# AI Provider (auto-detects in order: groq, openai, gemini)
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Model selection
AI_MODEL=llama-3.1-8b-instant  # for Groq
```

### AI Provider Priority
1. **Groq** (llama-3.1-8b-instant) - 14,400 free requests/day
2. **Gemini** (gemini-1.5-flash) - Backup option
3. **OpenAI** (gpt-4o-mini) - Fallback

## MCP Tools Pattern

All tools follow this pattern:
```python
async def tool_name(param1: type, param2: type) -> dict:
    """
    Tool description for AI.

    Args:
        param1: Description
        param2: Description

    Returns:
        dict: Result with status and data
    """
    # 1. Validate input
    # 2. Perform database operation
    # 3. Return formatted response
    return {"status": "success", "data": ...}
```

## Built-in MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `add_task` | Create new task | title (req), description (opt) |
| `list_tasks` | List user tasks | status (opt) |
| `complete_task` | Mark task complete | task_id (req) |
| `update_task` | Update task | task_id (req), title/desc (opt) |
| `delete_task` | Delete task | task_id (req) |
