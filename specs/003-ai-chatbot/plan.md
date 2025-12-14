# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `003-ai-chatbot` | **Date**: 2025-12-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot/spec.md`

**Note**: This plan extends Phase II architecture with AI agent capabilities, MCP tool integration, and conversational interface.

## Summary

This feature adds AI-powered conversational interface to the existing Phase II todo application. Users will interact with an AI agent through natural language to create, view, update, complete, and delete tasks. The agent uses Model Context Protocol (MCP) tools to execute task operations, maintaining stateless architecture with database-backed conversation history. OpenAI ChatKit provides the conversational UI, while OpenAI Agents SDK orchestrates agent behavior.

**Primary Requirement**: Users can manage their entire task workflow through natural language conversation instead of traditional CRUD forms.

**Technical Approach**: Stateless AI agent endpoint integrated with existing FastAPI backend, exposing task CRUD operations as MCP tools, persisting conversation state to PostgreSQL, and rendering chat interface via OpenAI ChatKit in Next.js frontend.

## Technical Context

**Language/Version**:
- Backend: Python 3.13+ (existing)
- Frontend: TypeScript 5+ with Next.js 15 (existing)

**Primary Dependencies**:
- Backend:
  - `openai` (>= 1.0.0) - OpenAI Agents SDK for agent orchestration
  - `mcp` (>= 1.0.0) - Official Model Context Protocol SDK
  - Existing: FastAPI 0.109+, SQLAlchemy 2.0+, asyncpg
- Frontend:
  - `@openai/chatkit` - OpenAI's conversational UI components
  - Existing: Next.js 15, React 18, Tailwind CSS

**Storage**:
- Neon PostgreSQL (existing) with two new tables:
  - `conversations` (user_id, conversation_id, created_at, updated_at)
  - `messages` (message_id, conversation_id, role, content, created_at)
- Existing `users` and `tasks` tables unchanged

**Testing**:
- Backend: pytest with async support for MCP tools and agent integration
- Frontend: Jest + React Testing Library for ChatKit components
- Integration: Multi-turn conversation flow tests

**Target Platform**:
- Backend: Linux server (existing deployment)
- Frontend: Vercel (existing deployment)
- AI Service: OpenAI API (cloud)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- AI response latency: < 3 seconds for 95% of requests
- Conversation history load: < 2 seconds for 50 messages
- Token usage: 100-500 tokens per conversation turn
- Concurrent conversations: 100+ simultaneous users

**Constraints**:
- Stateless agent design (any server instance handles any request)
- Must preserve all Phase II functionality
- Must enforce same data isolation as Phase II
- Token budget management (prevent runaway costs)
- OpenAI API rate limits

**Scale/Scope**:
- New endpoints: 2 (POST /api/chat, GET /api/conversations)
- MCP tools: 5 (add_task, list_tasks, complete_task, update_task, delete_task)
- New database tables: 2 (conversations, messages)
- New frontend pages: 1 (/chat)
- Estimated LOC: 1500 backend, 800 frontend

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Specific Principles (from constitution v3.0.0)

✅ **Stateless Agent Design**:
- Agent endpoints have no in-memory session state
- Conversation history loaded from database on each request
- Plan: Chat endpoint loads messages from DB, passes to agent, saves response

✅ **MCP Tool Integration**:
- Task operations exposed as MCP tools with user_id validation
- Plan: 5 MCP tools wrapping existing CRUD functions from Phase II

✅ **Conversation State Management**:
- Conversations and messages tables in database
- Plan: Alembic migration adds both tables with proper indexes

✅ **Natural Language Processing**:
- AI agent interprets intent and selects appropriate tools
- Plan: Agent configured with system prompt defining tool usage patterns

✅ **Technology Stack (Phase III)**:
- OpenAI Agents SDK: ✅ Planned
- MCP SDK: ✅ Planned
- OpenAI ChatKit: ✅ Planned
- Phase II stack preserved: ✅ No breaking changes

✅ **Code Quality Standards**:
- Agent behavior documented in spec: ✅ Complete
- Rate limiting on chat endpoints: ✅ Planned in implementation
- Token usage tracking: ✅ Planned in agent service
- User_id validation on all tools: ✅ Required in tool specs

### Phase Transition Rules

✅ **Phase II Complete**: All 6 user stories implemented, web CRUD functional

✅ **Migration ADR**: Created (ADR-002)

✅ **Backward Compatibility**: Phase II endpoints and UI remain unchanged

✅ **Constitution Updated**: v2.0.0 → v3.0.0

**GATE STATUS**: ✅ PASSED - All Phase III principles satisfied, ready for implementation

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot/
├── spec.md              # Feature specification (/sp.specify output) ✅
├── plan.md              # This file (/sp.plan output) ✅
├── research.md          # Technology decisions and best practices ⏳
├── data-model.md        # Database schema extensions ⏳
├── quickstart.md        # Development setup guide ⏳
├── contracts/           # MCP tool specifications ⏳
│   ├── add-task.json
│   ├── list-tasks.json
│   ├── complete-task.json
│   ├── update-task.json
│   └── delete-task.json
├── checklists/
│   └── requirements.md  # Specification quality checklist ✅
└── tasks.md             # Phase 2 output (/sp.tasks - not yet created)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── chat.py              # NEW: POST /api/chat endpoint
│   │   └── conversations.py     # NEW: GET /api/conversations endpoint
│   ├── services/
│   │   └── agent_service.py     # NEW: Agent orchestration logic
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py            # NEW: MCP server integration
│   │   └── tools/               # NEW: MCP tool implementations
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── update_task.py
│   │       └── delete_task.py
│   ├── models/
│   │   ├── conversation.py      # NEW: Conversation model
│   │   └── message.py           # NEW: Message model
│   ├── schemas/
│   │   ├── chat.py              # NEW: Chat request/response schemas
│   │   └── conversation.py      # NEW: Conversation schemas
│   └── crud/
│       ├── conversation.py      # NEW: Conversation CRUD operations
│       └── message.py           # NEW: Message CRUD operations
├── alembic/versions/
│   └── xxx_add_conversations.py # NEW: Migration for conversations/messages
└── tests/
    ├── test_mcp_tools.py        # NEW: MCP tool unit tests
    ├── test_agent.py            # NEW: Agent integration tests
    └── test_chat_api.py         # NEW: Chat endpoint tests

frontend/
├── app/
│   └── chat/
│       └── page.tsx             # NEW: Chat interface page
├── components/
│   └── chat/
│       ├── chat-interface.tsx   # NEW: ChatKit wrapper component
│       └── message-list.tsx     # NEW: Message history display
└── lib/
    └── chat-client.ts           # NEW: Chat API client functions
```

**Structure Decision**: Extends existing web application structure (frontend/backend). New chat functionality added as independent modules alongside existing Phase II code. MCP tools organized in dedicated `backend/app/mcp/` directory. Conversation management follows existing CRUD pattern (models → schemas → CRUD → API).

## Complexity Tracking

> No constitution violations - this section intentionally left empty. Phase III adheres to all architectural principles.

## Phase 0: Research & Technology Decisions

**Purpose**: Resolve technical unknowns and establish best practices for AI agent integration.

### Research Tasks

1. **OpenAI Agents SDK Integration Patterns**
   - How to structure stateless agent with conversation history
   - Best practices for agent prompt engineering
   - Error handling and fallback strategies
   - Token usage optimization techniques

2. **MCP Server Architecture**
   - FastAPI integration vs standalone MCP server
   - Tool registration and lifecycle management
   - Authentication/authorization patterns for MCP tools
   - Error propagation from tools to agent

3. **OpenAI ChatKit Setup**
   - Domain allowlist configuration requirements
   - Message streaming implementation
   - Markdown rendering configuration
   - Integration with existing Next.js app

4. **Conversation State Management**
   - Optimal database schema for messages (JSONB vs individual columns)
   - Indexing strategy for fast conversation retrieval
   - Pagination patterns for long conversation histories
   - Conversation lifecycle (creation, archival, deletion)

5. **Security Patterns**
   - Prompt injection prevention techniques
   - User data isolation in conversational context
   - Rate limiting strategies for AI endpoints
   - Token budget enforcement mechanisms

**Output**: `research.md` documenting decisions, alternatives considered, and implementation approach for each area.

## Phase 1: Design & Contracts

### Data Model Extensions

**Purpose**: Extend Phase II schema with conversation persistence.

**New Tables**:

1. **conversations**
   - Primary key: `id` (integer, auto-increment)
   - Foreign key: `user_id` (integer, references users.id)
   - `created_at` (timestamp, default now())
   - `updated_at` (timestamp, default now(), on update now())
   - Index: `user_id` (for filtering user's conversations)

2. **messages**
   - Primary key: `id` (integer, auto-increment)
   - Foreign key: `conversation_id` (integer, references conversations.id, on delete cascade)
   - `role` (enum: 'user' | 'assistant')
   - `content` (text)
   - `created_at` (timestamp, default now())
   - Index: `conversation_id` (for loading conversation history)
   - Index: composite (`conversation_id`, `created_at`) for ordered retrieval

**Relationships**:
- User → Conversations (one-to-many)
- Conversation → Messages (one-to-many, cascade delete)
- Messages reference Tasks indirectly through conversation context (no foreign key)

**Output**: `data-model.md` with complete schema, indexes, and relationships.

### API Contracts

**Purpose**: Define MCP tool specifications and chat endpoint contracts.

**MCP Tool Contracts** (`contracts/` directory):

Each tool spec includes:
- Tool name and description
- Input parameters (JSON schema)
- Output format (JSON schema)
- Error responses
- Authorization requirements (user_id validation)

1. **add_task.json**
   ```json
   {
     "name": "add_task",
     "description": "Create a new task for the user",
     "parameters": {
       "user_id": "integer (required)",
       "title": "string (required, max 500 chars)",
       "description": "string (optional, max 10000 chars)"
     },
     "returns": {
       "task_id": "integer",
       "status": "created",
       "title": "string"
     }
   }
   ```

2. **list_tasks.json**
   ```json
   {
     "name": "list_tasks",
     "description": "Retrieve user's tasks with optional filtering",
     "parameters": {
       "user_id": "integer (required)",
       "status": "string (optional: 'all' | 'pending' | 'completed')"
     },
     "returns": {
       "tasks": "array of task objects"
     }
   }
   ```

3. **complete_task.json**, **update_task.json**, **delete_task.json** (similar structure)

**Chat API Endpoint**:

```
POST /api/chat
Request:
  {
    "conversation_id": integer (optional, creates new if omitted),
    "message": string (required, user's input)
  }
Response:
  {
    "conversation_id": integer,
    "response": string (AI assistant's response),
    "tool_calls": array (tools invoked by agent)
  }
```

**Output**: JSON schemas in `contracts/` directory + OpenAPI spec updates.

### Quickstart Guide

**Purpose**: Development setup instructions for Phase III.

**Covers**:
1. OpenAI API key configuration
2. Installing new dependencies (`openai`, `mcp`, `@openai/chatkit`)
3. Running database migrations
4. Configuring ChatKit domain allowlist
5. Testing MCP tools individually
6. Testing chat endpoint with sample conversations
7. Debugging agent behavior (viewing tool calls, prompt logs)

**Output**: `quickstart.md` in specs directory.

### Agent Context Update

**Purpose**: Update agent-specific configuration with Phase III technologies.

Will add to appropriate agent context file:
- OpenAI Agents SDK patterns
- MCP tool registration
- ChatKit component usage
- Conversation state management patterns

**Output**: Updated agent context file (e.g., `.claude/AGENTS.md` or similar).

## Phase 2: Task Generation

**Not part of /sp.plan - this phase executes when user runs `/sp.tasks`**

The tasks command will generate actionable task breakdown with:
- Alembic migration tasks (conversations, messages tables)
- MCP tool implementation tasks (5 tools)
- Agent service implementation
- Chat API endpoint implementation
- ChatKit frontend integration
- Testing tasks (unit, integration, manual)
- Documentation tasks

See `/sp.tasks` command for task generation.

## Implementation Sequence

**Recommended order** (from ADR-002):

1. **Database Schema** (Phase 1)
   - Create migration
   - Add conversations and messages tables
   - Run migration on development database

2. **MCP Tools** (Phase 1-2)
   - Implement 5 tools wrapping existing CRUD
   - Add user_id validation to each tool
   - Unit test each tool independently

3. **Agent Service** (Phase 2)
   - Set up OpenAI Agents SDK
   - Configure agent with MCP tools
   - Implement conversation history loading
   - Add chat endpoint to FastAPI

4. **Frontend ChatKit** (Phase 2)
   - Install ChatKit package
   - Configure domain allowlist
   - Create chat page and components
   - Implement message streaming

5. **Testing & Integration** (Phase 2)
   - Test each MCP tool
   - Test multi-turn conversations
   - Test stateless operation
   - Test data isolation

## Dependencies

**External Services**:
- OpenAI API (GPT-4 or compatible model)
- Existing Neon PostgreSQL database
- Existing authentication system

**Internal Dependencies**:
- Phase II task CRUD functions (reused by MCP tools)
- Phase II authentication middleware (protects chat endpoints)
- Phase II database models (tasks, users)

**Development Environment**:
- OpenAI API key with sufficient quota
- Domain allowlist configured for ChatKit
- Python 3.13+ with async support
- Node.js 18+ for frontend

## Success Metrics

Implementation complete when:
- ✅ All 5 MCP tools implemented and tested
- ✅ Agent correctly interprets 95%+ of single-intent messages
- ✅ Conversations persist across server restarts
- ✅ ChatKit UI deployed and functional
- ✅ All Phase II features still working
- ✅ Data isolation enforced in chat interface
- ✅ Integration tests covering multi-turn flows pass
- ✅ Token usage tracking in place
- ✅ Rate limiting configured
- ✅ Documentation complete (quickstart, contracts)

## Risk Mitigation

**Risk 1**: OpenAI API availability/latency
- **Mitigation**: Implement timeout handling, fallback messaging, retry logic

**Risk 2**: Token costs exceeding budget
- **Mitigation**: Token usage tracking, rate limiting, conversation length limits

**Risk 3**: Prompt injection attacks
- **Mitigation**: Input sanitization, system prompt hardening, user_id validation

**Risk 4**: Agent misinterpreting user intent
- **Mitigation**: Comprehensive testing, clarification prompts, fallback to suggestions

**Risk 5**: ChatKit domain allowlist configuration issues
- **Mitigation**: Test on development domain first, document setup process

## Next Steps

After plan approval:
1. **Run `/sp.tasks`** to generate detailed task breakdown
2. **Review research.md** to validate technology decisions
3. **Review data-model.md** to confirm schema design
4. **Review contracts/** to validate MCP tool specs
5. **Run `/sp.implement`** to execute tasks
