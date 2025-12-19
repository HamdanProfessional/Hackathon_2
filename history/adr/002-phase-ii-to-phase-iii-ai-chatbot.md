# ADR-002: Phase II to Phase III Migration - AI-Powered Chatbot Integration

> **Scope**: Complete architectural migration from static web application to AI-augmented conversational interface with Model Context Protocol (MCP) integration.

- **Status:** Accepted
- **Date:** 2025-12-13
- **Feature:** Phase III - AI-Powered Todo Chatbot
- **Context:** Phase II (Modular Monolith) complete. Transitioning to Phase III to add AI agent capabilities for natural language task management through conversational interface.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Long-term architectural shift to AI-first interactions
     2) Alternatives: YES - Multiple AI frameworks and protocols considered
     3) Scope: YES - Cross-cutting changes to frontend, backend, and data model
-->

## Decision

We will integrate AI agent capabilities into the existing Phase II todo application by:

**AI Agent Layer:**
- **AI Framework**: OpenAI Agents SDK for agent orchestration
- **AI Model**: GPT-4 (via OpenAI API) or Claude (via OpenAI-compatible endpoint)
- **Agent Architecture**: Stateless agent with database-backed conversation history
- **Tool Protocol**: Model Context Protocol (MCP) SDK for exposing task operations

**Conversational Interface:**
- **Frontend**: OpenAI ChatKit for conversational UI
- **Chat Endpoint**: POST /api/chat (stateless, loads history from DB)
- **Conversation Persistence**: New database tables (conversations, messages)
- **Message Streaming**: Real-time streaming responses for better UX

**MCP Tool Integration:**
- **Tools Exposed**: add_task, list_tasks, complete_task, update_task, delete_task
- **Tool Server**: Integrated FastAPI MCP server (not standalone)
- **Data Isolation**: All tools require user_id validation
- **State Management**: Stateless tools backed by database

**Architecture Characteristics:**
- Stateless agent design (horizontal scalability)
- Database-backed conversation history (resilient to restarts)
- Async/await throughout agent pipeline
- Integration with existing Phase II auth + task CRUD endpoints

## Consequences

### Positive

1. **Natural Language Interface**: Users can manage tasks through conversation ("Add groceries to my list", "What's pending?")
2. **AI-Powered Intelligence**: Agent can interpret ambiguous requests, suggest task improvements, provide reminders
3. **Stateless Scalability**: Any server instance can handle any request (conversation state in DB)
4. **MCP Standardization**: Tools follow industry standard protocol, reusable across AI systems
5. **Phase II Preservation**: Existing web UI remains fully functional, chatbot is additive
6. **Conversation History**: Full context persistence allows resuming conversations after server restart
7. **Multi-Turn Interactions**: Agent can ask clarifying questions, handle complex multi-step operations

### Negative

1. **Increased Complexity**: New concerns (token management, agent behavior testing, prompt engineering)
2. **External Dependency**: Requires OpenAI API access (costs, rate limits, availability)
3. **Database Growth**: Conversation messages accumulate over time (storage management needed)
4. **Latency**: AI inference adds latency vs. direct API calls (1-3 seconds per response)
5. **Non-Determinism**: AI responses may vary for same input (testing complexity)
6. **Token Costs**: Operating costs increase with conversation length and usage
7. **Security Surface**: New attack vectors (prompt injection, jailbreaking, data exfiltration via agent)

## Alternatives Considered

### Alternative 1: LangChain + Custom Tools
**Stack**: LangChain framework + Custom Python functions for task operations

**Why Rejected**:
- LangChain adds unnecessary abstraction complexity
- MCP provides standardized protocol vs. custom integration
- OpenAI Agents SDK more lightweight and direct
- LangChain's async support less mature than OpenAI SDK

### Alternative 2: Claude AI SDK + Anthropic MCP
**Stack**: Claude AI SDK + Anthropic's MCP implementation

**Why Rejected**:
- Less documentation and community support than OpenAI SDK
- MCP implementations compatible, but OpenAI SDK better integrated with ChatKit
- Can migrate to Claude via OpenAI-compatible endpoint if needed
- Anthropic MCP servers designed for standalone processes (we want integrated)

### Alternative 3: No MCP - Direct Function Calling
**Stack**: OpenAI function calling without MCP protocol

**Why Rejected**:
- MCP provides standardized tool schema (reusable across platforms)
- MCP server can be consumed by other AI systems (not locked to OpenAI)
- Function calling requires more boilerplate than MCP tools
- MCP future-proofs for multi-agent scenarios (Phase V)

### Alternative 4: Stateful Agent (In-Memory Session)
**Stack**: In-memory conversation state managed by server

**Why Rejected**:
- Breaks horizontal scalability (sticky sessions required)
- Conversation lost on server restart (poor UX)
- Requires session management complexity (expiration, cleanup)
- Database-backed approach aligns with Phase II stateless architecture

### Alternative 5: Standalone MCP Server
**Stack**: Separate MCP server process communicating with FastAPI

**Why Rejected**:
- Adds deployment complexity (two processes to manage)
- Network latency between MCP server and FastAPI
- Authentication/authorization duplication across services
- Premature microservices pattern (appropriate for Phase IV, not III)

## Migration Strategy

**Phase 1: Database Schema Extension**
1. Create conversations table (user_id, conversation_id, created_at, updated_at)
2. Create messages table (conversation_id, role, content, created_at)
3. Run Alembic migrations to extend Phase II schema

**Phase 2: MCP Tools Implementation**
1. Install MCP SDK in backend (pip install mcp)
2. Create backend/app/mcp_tools/ directory
3. Implement 5 MCP tools wrapping existing CRUD operations
4. Add user_id validation to all tools
5. Define JSON schemas for tool parameters

**Phase 3: Agent Integration**
1. Install OpenAI Agents SDK (pip install openai-agents)
2. Create backend/app/services/agent_service.py
3. Implement stateless agent with conversation history loading
4. Configure agent with MCP tools and system prompt
5. Add POST /api/chat endpoint to FastAPI

**Phase 4: Frontend ChatKit Integration**
1. Install OpenAI ChatKit in frontend (npm install @openai/chatkit)
2. Configure domain allowlist in OpenAI platform
3. Create frontend/app/chat/page.tsx with ChatKit component
4. Implement message streaming and rendering
5. Add navigation link from dashboard to chat

**Phase 5: Testing & Validation**
1. Test each MCP tool individually (unit tests)
2. Test agent conversation flows (integration tests)
3. Test stateless operation (server restart mid-conversation)
4. Test data isolation (user A can't access user B's conversations)
5. Load testing for concurrent conversations

## Data Migration

**No data migration required** - Phase III is additive:
- Existing users, tasks tables remain unchanged
- New conversations, messages tables added
- Existing Phase II web UI continues working
- Chatbot interface is new feature, not replacement

## Backward Compatibility

**Fully Backward Compatible:**
- All Phase II endpoints remain functional
- Web UI (dashboard, task CRUD) untouched
- Authentication system unchanged
- Database schema extended, not modified

**New Features:**
- /api/chat endpoint (new)
- /api/conversations endpoint (new)
- Chat UI (/chat page) (new)
- MCP tools (internal, not directly exposed)

## Success Criteria

Phase III complete when:
1. ✅ AI agent can create tasks via natural language ("Add buy groceries")
2. ✅ AI agent can list tasks with filtering ("Show me pending tasks")
3. ✅ AI agent can mark tasks complete ("Mark task 3 as done")
4. ✅ AI agent can update task details ("Change task 1 title to...")
5. ✅ AI agent can delete tasks ("Remove the meeting task")
6. ✅ Conversations persist across server restarts
7. ✅ Multi-user isolation (users can't access others' conversations)
8. ✅ ChatKit UI deployed and domain-allowlisted
9. ✅ All Phase II features still functional
10. ✅ Integration tests cover agent → MCP → database flow

## References

- Feature Spec: `specs/003-ai-chatbot/spec.md` (to be created)
- Implementation Plan: `specs/003-ai-chatbot/plan.md` (to be created)
- Tasks: `specs/003-ai-chatbot/tasks.md` (to be created)
- Related ADRs: ADR-001 (Phase I → Phase II Migration)
- Constitution: v3.0.0 (Phase III standards)
- Requirements: Phase III section in requirements.md
