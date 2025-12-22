# Project Constants

## Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://frontend-l0e30jmlq-hamdanprofessionals-projects.vercel.app |
| Backend | https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app |

## AI Configuration

| Setting | Value |
|---------|-------|
| Provider | Groq (Primary) |
| Model | llama-3.1-8b-instant |
| API Base | https://api.groq.com/openai/v1 |
| Free Tier | 14,400 requests/day |
| Fallback | Gemini → OpenAI → Grok |

## Database

| Setting | Value |
|---------|-------|
| Type | PostgreSQL (Neon) |
| Schema | SQLModel |
| Migrations | Alembic |
| Latest Migration | 004_fix_message_role_enum_to_varchar |

## Project Structure

```
Hackathon_2/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   ├── alembic/      # Database migrations
│   └── tests/        # Test files (organized)
├── frontend/         # Next.js frontend
│   ├── app/         # App Router pages
│   ├── components/  # React components
│   └── lib/         # Utilities (api.ts)
├── tests/            # Shared test files
├── specs/            # Feature specifications
└── .claude/          # Claude configuration
    ├── memory/       # Project memory
    └── settings.local.json
```

## Phase III Features Implemented

| Feature | Status | Location |
|---------|--------|----------|
| AI Chat Interface | ✅ | `/chat` page |
| Dashboard Chat Widget | ✅ | ChatWidget component |
| Delete Conversations | ✅ | chat-interface.tsx |
| MCP Tools | ✅ | mcp_tools.py |
| Stateless Agent | ✅ | agent.py |
| Conversation Persistence | ✅ | conversations/messages tables |

## Test Credentials

| Field | Value |
|-------|-------|
| Email | test1@test.com |
| Password | Test1234 |

## MCP Tools Available

- `add_task` - Create a new task
- `list_tasks` - List all tasks for authenticated user
- `complete_task` - Mark task as complete
- `update_task` - Update task details
- `delete_task` - Delete a task

## Git Branches

| Branch | Purpose |
|--------|---------|
| main | Development branch |
| master | Production PR target |

## Key Files

- `backend/app/config.py` - AI provider configuration
- `backend/app/ai/agent.py` - Stateless agent implementation
- `backend/app/ai/mcp_tools.py` - MCP tool definitions
- `frontend/components/chat/chat-interface.tsx` - Main chat component
- `frontend/lib/api.ts` - API client with JWT auth
- `specs/003-ai-chatbot/spec.md` - Phase III specification
