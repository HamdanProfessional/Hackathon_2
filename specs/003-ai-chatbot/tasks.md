# Implementation Tasks: AI-Powered Todo Chatbot

**Feature**: Phase III - AI-Powered Todo Chatbot
**Branch**: `003-ai-chatbot`
**Status**: Ready for Implementation
**Generated**: 2025-12-13

**References**:
- Spec: [spec.md](./spec.md)
- Plan: [plan.md](./plan.md)
- Data Model: [data-model.md](./data-model.md)
- Contracts: [contracts/](./contracts/)
- Research: [research.md](./research.md)
- Quickstart: [quickstart.md](./quickstart.md)

---

## Task Summary

**Total Tasks**: 89
**Phases**: 9 (Setup, Foundational, 6 User Stories, Polish)
**Independent User Stories**: 6 (all independently testable after Foundational phase)
**Parallelizable Tasks**: 47 tasks marked [P]

**User Story Priority**:
- **P1 (MVP)**: US1 (Task Creation), US2 (Task Listing), US6 (Conversation Persistence)
- **P2**: US3 (Task Completion)
- **P3**: US4 (Task Updates), US5 (Task Deletion)

---

## Phase 1: Setup & Prerequisites

**Goal**: Install dependencies, configure environment, prepare infrastructure for Phase III development

**Tasks**:

- [X] T001 [P] Install backend dependencies: add `openai>=1.0.0` and `mcp>=1.0.0` to backend/requirements.txt and run pip install
- [X] T002 [P] Install frontend dependencies: run `npm install @openai/chatkit` in frontend directory
- [X] T003 [P] Create backend environment variables in backend/.env: OPENAI_API_KEY, OPENAI_MODEL (gpt-4), MAX_TOKENS_PER_DAY (50000)
- [X] T004 [P] Create frontend environment variables in frontend/.env.local: NEXT_PUBLIC_OPENAI_DOMAIN_KEY (empty for localhost)
- [X] T005 Create backend/app/mcp/ directory structure: __init__.py, server.py, tools/ subdirectory
- [X] T006 Create backend/app/services/ directory if not exists
- [X] T007 Create frontend/components/chat/ directory structure
- [X] T008 Create frontend/lib/chat-client.ts placeholder file
- [X] T009 [P] Create specs/003-ai-chatbot/contracts/ directory and copy MCP tool JSON specs (already created)
- [X] T010 [P] Review quickstart.md to understand Phase III development workflow

**Checkpoint**: Development environment configured, dependencies installed, directory structure ready

---

## Phase 2: Foundational - Database & MCP Infrastructure

**Goal**: Extend database schema with conversation tables and create MCP tool foundation (BLOCKS all user stories)

### Database Migration

- [X] T011 Create Alembic migration file: backend/alembic/versions/xxx_add_conversations_and_messages.py
- [X] T012 Add conversations table to migration: id (serial pk), user_id (fk users.id), created_at, updated_at with indexes
- [X] T013 Add messages table to migration: id (serial pk), conversation_id (fk conversations.id cascade), role (enum user/assistant), content (text), created_at
- [X] T014 Add composite index to migration: idx_messages_conversation_created on (conversation_id, created_at)
- [X] T015 Add trigger to migration: update_conversation_timestamp() function that updates conversations.updated_at when message inserted
- [X] T016 Test migration: run `alembic upgrade head` on development database and verify tables created
- [X] T017 Test migration rollback: run `alembic downgrade -1` and verify tables dropped, then re-upgrade

### Database Models

- [X] T018 [P] Create backend/app/models/conversation.py: Conversation model with relationships to User and Messages
- [X] T019 [P] Create backend/app/models/message.py: Message model with relationship to Conversation and CHECK constraint on role
- [X] T020 [P] Update backend/app/models/user.py: add conversations relationship (one-to-many with cascade delete)

### Pydantic Schemas

- [X] T021 [P] Create backend/app/schemas/conversation.py: ConversationResponse schema with id, user_id, created_at, updated_at
- [X] T022 [P] Create backend/app/schemas/chat.py: ChatRequest (conversation_id optional, message required) and ChatResponse (conversation_id, response, tool_calls array)
- [X] T023 [P] Create backend/app/schemas/message.py: MessageResponse schema with role, content, created_at

### CRUD Operations

- [X] T024 [P] Create backend/app/crud/conversation.py: create_conversation, get_conversation_by_id, get_user_conversations functions
- [X] T025 [P] Create backend/app/crud/message.py: create_message, get_conversation_messages, delete_conversation_messages functions

**Checkpoint**: Database schema extended, models created, CRUD operations ready. All user stories can now build on this foundation.

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1)

**Goal**: Users can create tasks by typing natural language in chat interface

**Independent Test**: User opens /chat, types "Add buy groceries to my list", sees AI confirmation, opens /dashboard and sees "Buy groceries" task listed

### Backend - MCP Tool

- [X] T026 [P] [US1] Create backend/app/mcp/tools/add_task.py: implement add_task() async function wrapping existing create_task CRUD
- [X] T027 [US1] Add user_id validation to add_task tool: raise Unauthorized if user_id missing or invalid
- [X] T028 [US1] Add input validation to add_task tool: title required (1-500 chars), description optional (max 10000 chars)
- [X] T029 [US1] Return structured response from add_task: {"task_id": int, "status": "created", "title": str}

### Backend - Agent Service

- [X] T030 [US1] Create backend/app/services/agent_service.py: AgentService class with __init__(user_id, openai_api_key)
- [X] T031 [US1] Implement create_agent_with_tools() in agent_service.py: configure OpenAI Agents SDK with add_task tool registered
- [X] T032 [US1] Add system prompt to agent configuration: define role as task management assistant, security rules, tool usage patterns
- [X] T033 [US1] Implement process_message() method: takes message history, calls agent, returns response with tool_calls

### Backend - Chat API

- [X] T034 [US1] Create backend/app/api/chat.py: POST /api/chat endpoint with authentication dependency
- [X] T035 [US1] Implement conversation creation logic: if conversation_id not provided, create new conversation for user
- [X] T036 [US1] Implement message history loading: load last 50 messages from conversation ordered by created_at
- [X] T037 [US1] Implement agent invocation: pass history + new user message to AgentService.process_message()
- [X] T038 [US1] Implement message persistence: save user message and agent response to messages table
- [X] T039 [US1] Return ChatResponse: conversation_id, agent response text, tool_calls array

### Frontend - Chat Interface

- [X] T040 [P] [US1] Create frontend/app/chat/page.tsx: authenticated chat page with ChatKit component
- [X] T041 [P] [US1] Create frontend/components/chat/chat-interface.tsx: wrapper for ChatKit with API integration
- [X] T042 [P] [US1] Create frontend/lib/chat-client.ts: sendMessage(conversationId, message) function calling POST /api/chat
- [X] T043 [US1] Integrate authentication: load JWT token and pass in Authorization header to chat API
- [X] T044 [US1] Implement message streaming: configure ChatKit streaming=true for real-time responses
- [X] T045 [US1] Add markdown rendering: configure ChatKit renderMarkdown=true for formatted responses

### Integration

- [X] T046 [US1] Add navigation link to chat: update frontend/app/dashboard/page.tsx header with link to /chat
- [X] T047 [US1] Test US1 end-to-end: create task via chat "Add test task", verify appears in dashboard, verify conversation persists

**Manual Test Scenarios for US1**:
1. Open /chat, type "Add buy milk to my list", verify confirmation message
2. Open /dashboard, verify "Buy milk" task exists
3. Return to /chat, type "Add finish report. Description: Q4 analysis", verify both title and description saved
4. Try ambiguous input "add something", verify agent asks clarifying question
5. Refresh /chat page, verify conversation history loads

**Checkpoint**: MVP deliverable! Users can create tasks via natural language and see them in traditional UI.

---

## Phase 4: User Story 2 - Conversational Task Listing (Priority: P1)

**Goal**: Users can ask to see their tasks using natural language queries

**Independent Test**: User types "Show me my tasks" in chat, sees all pending tasks listed in response

### Backend - MCP Tool

- [X] T048 [P] [US2] Create backend/app/mcp/tools/list_tasks.py: implement list_tasks() async function wrapping get_tasks_by_user CRUD
- [X] T049 [US2] Add user_id validation to list_tasks tool: ensure only user's tasks returned
- [X] T050 [US2] Add status filter parameter to list_tasks: support "all", "pending", "completed" values (default "all")
- [X] T051 [US2] Return structured response from list_tasks: {"tasks": array, "count": int}
- [X] T052 [US2] Format task objects in response: include id, title, description, completed, created_at for each task

### Backend - Agent Integration

- [X] T053 [US2] Register list_tasks tool with agent in agent_service.py: add to tools array in create_agent_with_tools()
- [X] T054 [US2] Update system prompt: add examples of when to use list_tasks (user says "show", "what's", "list", etc.)
- [X] T055 [US2] Add intent recognition patterns for listing: teach agent to detect queries vs. commands

### Frontend - Message Display

- [X] T056 [P] [US2] Create frontend/components/chat/message-list.tsx: component for rendering task lists in chat
- [X] T057 [US2] Format task list responses: render tasks as bullet list with checkmarks for completed items
- [X] T058 [US2] Add empty state handling: friendly message when no tasks exist ("Your task list is empty!")

### Integration

- [X] T059 [US2] Test US2 end-to-end: create 3 tasks (2 pending, 1 complete), ask "What's on my list?", verify all 3 shown
- [X] T060 [US2] Test filtering: ask "Show me completed tasks", verify only completed task shown
- [X] T061 [US2] Test empty state: delete all tasks, ask "What do I need to do?", verify helpful empty response

**Manual Test Scenarios for US2**:
1. Create tasks via web UI first (2 pending, 1 completed)
2. In chat, type "What's on my todo list?", verify sees all tasks
3. Type "Show me completed tasks", verify sees only completed
4. Type "What's pending?", verify sees only 2 pending tasks
5. Type "What did I add today?", verify date filtering works

**Checkpoint**: Users can view their tasks conversationally. Core CRUD (Create + Read) working via chat.

---

## Phase 5: User Story 6 - Multi-Turn Conversation Persistence (Priority: P1)

**Goal**: Conversation history persists across page refreshes and server restarts

**Independent Test**: User starts conversation, discusses tasks, refreshes browser, returns to /chat, sees full conversation history and can continue

**Note**: Much of US6 infrastructure already built in US1. These tasks validate and enhance persistence.

### Backend - Conversation Management

- [X] T062 [P] [US6] Add conversation pagination to crud/message.py: support offset/limit for very long conversations
- [X] T063 [P] [US6] Implement get_user_conversations() in crud/conversation.py: return user's conversations sorted by updated_at desc
- [X] T064 [US6] Add conversation history trimming: load only last 50 messages to prevent token budget overflow
- [X] T065 [US6] Verify stateless operation: restart backend server mid-conversation, verify next message continues seamlessly

### Backend - API Endpoints

- [X] T066 [P] [US6] Create backend/app/api/conversations.py: GET /api/conversations endpoint returning user's conversation list
- [X] T067 [US6] Add conversation details endpoint: GET /api/conversations/{id} with ownership validation
- [X] T068 [US6] Register conversations router in backend/app/main.py: add router with /api prefix

### Frontend - History Loading

- [X] T069 [US6] Implement loadConversationHistory() in chat-client.ts: fetch GET /api/conversations/{id} on chat page mount
- [X] T070 [US6] Display conversation history in ChatKit: pass loaded messages to ChatKit initialMessages prop
- [X] T071 [US6] Add conversation list sidebar: show user's recent conversations with timestamps (optional enhancement)

### Integration

- [X] T072 [US6] Test persistence across refresh: start conversation, add 3 tasks, refresh page, verify all messages visible
- [X] T073 [US6] Test multi-turn context: create task "Buy milk", then say "Mark it as done", verify agent understands "it" refers to milk task
- [X] T074 [US6] Test server restart: have active conversation, restart backend, send new message, verify conversation continues
- [X] T075 [US6] Test long conversation: create 60-message conversation, verify only last 50 loaded (pagination working)

**Manual Test Scenarios for US6**:
1. Start new conversation, add 2 tasks, ask to list tasks, refresh browser
2. Verify all 3 messages (2 add commands + 1 list query) still visible
3. Continue conversation with "What did I just add?", verify agent references previous messages
4. Close browser completely, reopen /chat, verify full conversation history loads
5. (If possible) Restart backend server, send new message, verify no errors

**Checkpoint**: P1 MVP COMPLETE! Users can create tasks, list tasks, and maintain conversation context. System is stateless and resilient.

---

## Phase 6: User Story 3 - Natural Language Task Completion (Priority: P2)

**Goal**: Users can mark tasks complete via natural language

**Independent Test**: User types "I finished the groceries task" in chat, sees confirmation, opens dashboard and sees task marked complete with strikethrough

### Backend - MCP Tool

- [X] T076 [P] [US3] Create backend/app/mcp/tools/complete_task.py: implement complete_task() async function wrapping toggle_task_completion CRUD
- [X] T077 [US3] Add user_id and task_id validation to complete_task tool
- [X] T078 [US3] Return structured response: {"task_id": int, "status": "completed"|"incomplete", "title": str}
- [X] T079 [US3] Handle task not found error: raise NotFoundException if task doesn't exist or doesn't belong to user

### Backend - Agent Integration

- [X] T080 [US3] Register complete_task tool with agent in agent_service.py
- [X] T081 [US3] Update system prompt: add examples for completion intent ("finished", "done", "mark complete")
- [X] T082 [US3] Add fuzzy task matching: teach agent to find task by partial title match when user doesn't specify ID

### Integration

- [X] T083 [US3] Test US3 end-to-end: create task via chat, say "I finished [task name]", verify marked complete in dashboard
- [X] T084 [US3] Test by ID: say "Mark task 3 as done", verify task 3 completed
- [X] T085 [US3] Test ambiguous reference: create 2 tasks with similar names, say "mark it done", verify agent asks which one

**Manual Test Scenarios for US3**:
1. Create task "Buy groceries" via chat
2. Type "I finished buying groceries", verify confirmation
3. Open dashboard, verify task has strikethrough/checkmark
4. Return to chat, type "Mark task 1 as incomplete", verify toggled back
5. Test partial match: "I'm done with the report" matches "Finish Q4 report"

**Checkpoint**: Complete task lifecycle via chat (Create → Read → Complete). Users rarely need web UI now.

---

## Phase 7: User Story 4 - Conversational Task Updates (Priority: P3)

**Goal**: Users can modify task details through natural language

**Independent Test**: User types "Change the groceries task to include fruits", sees confirmation, opens dashboard and sees updated description

### Backend - MCP Tool

- [X] T086 [P] [US4] Create backend/app/mcp/tools/update_task.py: implement update_task() async function wrapping update_task CRUD
- [X] T087 [US4] Add validation: require at least one field (title or description) to update
- [X] T088 [US4] Return structured response: {"task_id": int, "status": "updated", "title": str}

### Backend - Agent Integration

- [X] T089 [US4] Register update_task tool with agent
- [X] T090 [US4] Update system prompt: examples for update intent ("change", "modify", "update", "rename")
- [X] T091 [US4] Add clarification logic: if multiple fields mentioned, ask user to confirm which to update

### Integration

- [X] T092 [US4] Test US4 end-to-end: create task, say "Change [task] to [new title]", verify updated
- [X] T093 [US4] Test description update: "Add description to task 2: needs review", verify description added
- [X] T094 [US4] Test both fields: "Rename task to X and change description to Y", verify both updated

**Manual Test Scenarios for US4**:
1. Create task "Buy milk"
2. Type "Change buy milk to buy groceries", verify title updated
3. Type "Add description: need to get vegetables too", verify description added
4. Test multiple matches: "Update the meeting task" with 2 meeting tasks, verify agent asks which one

**Checkpoint**: Full edit capability via conversation. Users can refine tasks without leaving chat.

---

## Phase 8: User Story 5 - Natural Language Task Deletion (Priority: P3)

**Goal**: Users can delete tasks via chat with confirmation flow

**Independent Test**: User types "Delete the old notes task", agent asks confirmation, user confirms, task removed from dashboard

### Backend - MCP Tool

- [X] T095 [P] [US5] Create backend/app/mcp/tools/delete_task.py: implement delete_task() async function wrapping delete_task CRUD
- [X] T096 [US5] Return structured response: {"task_id": int, "status": "deleted", "title": str}

### Backend - Agent Integration

- [X] T097 [US5] Register delete_task tool with agent
- [X] T098 [US5] Update system prompt: CRITICAL - ALWAYS ask confirmation before calling delete_task tool
- [X] T099 [US5] Add confirmation flow pattern: agent must ask "Are you sure you want to delete [task]?" and wait for explicit "yes"

### Integration

- [X] T100 [US5] Test US5 end-to-end: create task, say "Delete [task]", verify agent asks confirmation, say "yes", verify deleted
- [X] T101 [US5] Test cancellation: say "Delete task", agent asks confirmation, say "no", verify task NOT deleted
- [X] T102 [US5] Test implicit confirmation: say "Delete task 5 please" (no prior context), verify agent still asks "Are you sure?"

**Manual Test Scenarios for US5**:
1. Create task "Old meeting notes"
2. Type "Delete old meeting notes task", wait for confirmation prompt
3. Verify agent asks "Are you sure you want to delete 'Old meeting notes'?"
4. Type "Yes", verify task deleted and dashboard shows it gone
5. Try again with "Cancel" or "No", verify task NOT deleted

**Checkpoint**: All CRUD operations complete via chat. Full feature parity with web UI.

---

## Phase 9: Polish, Security & Deployment

**Goal**: Production readiness, security hardening, error handling, testing, deployment

### Security & Rate Limiting

- [X] T103 [P] Add rate limiting to chat endpoint: use slowapi limiter @limiter.limit("30/minute") on POST /api/chat
- [X] T104 [P] Implement token budget tracking in agent_service.py: count tokens per user per day, enforce MAX_TOKENS_PER_DAY
- [X] T105 [P] Add input sanitization in chat endpoint: validate message length (max 1000 chars), strip suspicious patterns
- [X] T106 [P] Harden system prompt against injection: test with adversarial inputs ("ignore previous instructions"), ensure agent stays on task

### Error Handling

- [X] T107 Add timeout handling to agent calls: 10-second timeout with user-friendly error message
- [X] T108 Add retry logic for OpenAI API: max 2 retries for transient failures (rate limits, network errors)
- [X] T109 Add error responses for all MCP tools: TaskNotFound, Unauthorized, ValidationError with clear messages
- [X] T110 Add fallback messaging: if agent fails repeatedly, offer to redirect user to web UI

### Testing (Optional - only if explicitly requested)

- [X] T111 [P] Write pytest tests for add_task MCP tool: test success, validation errors, unauthorized access
- [X] T112 [P] Write pytest tests for list_tasks MCP tool: test filtering, empty results, user isolation
- [X] T113 [P] Write pytest tests for complete/update/delete tools
- [X] T114 [P] Write integration test for chat endpoint: mock OpenAI agent, test conversation flow
- [X] T115 [P] Write test for conversation persistence: create conversation, restart app (in-memory DB), verify history loads
- [X] T116 [P] Write frontend Jest tests for ChatInterface component: test message sending, history loading

### Frontend Polish

- [X] T117 [P] Add loading states to chat interface: show spinner while agent processing
- [X] T118 [P] Add error handling UI: display user-friendly error messages for network failures, API errors
- [X] T119 [P] Improve markdown rendering: test code blocks, lists, bold/italic formatting in agent responses
- [X] T120 [P] Add conversation management UI: list recent conversations, start new conversation button, delete old conversations
- [X] T121 [P] Mobile responsive design: test chat interface on mobile viewport, adjust layout if needed

### Documentation

- [X] T122 [P] Update backend README.md: document new environment variables (OPENAI_API_KEY, MAX_TOKENS_PER_DAY)
- [X] T123 [P] Update frontend README.md: document ChatKit setup, domain allowlist configuration
- [X] T124 [P] Create deployment guide: steps for deploying Phase III (Neon, Vercel, OpenAI config)
- [X] T125 [P] Update API documentation: add /api/chat and /api/conversations endpoints to FastAPI /docs

### Deployment

- [ ] T126 Verify all Phase II features still work: test login, register, task CRUD via web UI
- [ ] T127 Configure OpenAI ChatKit domain allowlist: deploy frontend to Vercel, add domain to OpenAI platform
- [ ] T128 Deploy backend to production: set environment variables, run migrations
- [ ] T129 Deploy frontend to production: configure NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- [ ] T130 Smoke test production: register new user, create tasks via chat, verify appear in dashboard

### Final Validation

- [ ] T131 Test all 6 user stories end-to-end on production
- [ ] T132 Verify data isolation: create second user, ensure cannot access first user's conversations or tasks
- [ ] T133 Load test chat endpoint: simulate 10 concurrent conversations, verify performance within SLAs (<3s response)
- [ ] T134 Monitor token usage: track costs for first week, adjust MAX_TOKENS_PER_DAY if needed

**Checkpoint**: Phase III production-ready and deployed. AI chatbot fully functional.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
  ↓
Phase 2 (Foundational) [BLOCKS all user stories]
  ↓
  ├─→ Phase 3 (US1) [P1] ─┐
  ├─→ Phase 4 (US2) [P1] ─┼─→ Phase 5 (US6) [P1] = MVP
  └─→ Phase 5 (US6) [P1] ─┘
       ↓
  ├─→ Phase 6 (US3) [P2] (independent after MVP)
  ├─→ Phase 7 (US4) [P3] (independent after MVP)
  └─→ Phase 8 (US5) [P3] (independent after MVP)
       ↓
  Phase 9 (Polish) [requires all user stories complete]
```

### User Story Independence

After Phase 2 (Foundational) complete:
- ✅ US1, US2, US6 can be developed in parallel (all P1)
- ✅ US3, US4, US5 can be developed in any order after MVP (P2/P3)

**Recommended MVP**: Complete only US1 + US2 + US6 first (15 tasks), deploy, gather user feedback before continuing.

### Parallel Execution Examples

**Within US1 (47 parallelizable tasks across all phases)**:
- T026-T029 (MCP tool) + T040-T042 (Frontend UI) can run in parallel
- T018-T020 (Models) + T021-T023 (Schemas) can run in parallel

**Across User Stories (after Foundational)**:
- US1 backend (T026-T039) + US2 backend (T048-T055) + US6 backend (T062-T068) = 3 parallel tracks
- US3 + US4 + US5 (all MCP tools) can be built simultaneously

---

## Implementation Strategy

### Suggested Approach: MVP-First Incremental Delivery

**Week 1**: Phase 1 + Phase 2 (Setup + Foundational)
- 25 tasks, ~2-3 days
- Deliverable: Database ready, MCP infrastructure in place

**Week 2**: Phase 3 + Phase 4 + Phase 5 (P1 User Stories = MVP)
- 44 tasks, ~4-5 days
- Deliverable: Users can create, list, and discuss tasks via chat with persistent conversations

**Week 3**: Phase 6 + Phase 7 + Phase 8 (P2/P3 User Stories)
- 27 tasks, ~3 days
- Deliverable: Complete CRUD via chat

**Week 4**: Phase 9 (Polish & Deployment)
- 31 tasks, ~3-4 days
- Deliverable: Production-ready, secure, tested, deployed

### Alternative: Story-by-Story (Maximum Independence)

1. Complete US1 entirely (T026-T047) → Deploy → Test
2. Complete US2 entirely (T048-T061) → Deploy → Test
3. Complete US6 entirely (T062-T075) → Deploy → Test
4. ...continue with remaining stories

This approach provides user value incrementally but may feel slower overall.

---

## Success Criteria (from spec.md)

Implementation complete when all success criteria met:

- ✅ SC-001: Users create tasks via chat in <10 seconds
- ✅ SC-002: 90% of operations succeed on first attempt without clarification
- ✅ SC-003: 95%+ intent recognition accuracy
- ✅ SC-004: Conversation history loads in <2 seconds (50 messages)
- ✅ SC-005: Context maintained across page refreshes
- ✅ SC-006: Multi-turn conversations (3+ exchanges) work seamlessly
- ✅ SC-007: Natural language task references work 85%+ of the time
- ✅ SC-008: Max 1 clarification per 5 requests (not over-clarifying)
- ✅ SC-009: Zero data isolation breaches
- ✅ SC-010: AI responses in <3 seconds (95% of requests)
- ✅ SC-011: Real-time consistency between chat and web UI
- ✅ SC-012: Graceful handling of ambiguous/out-of-scope requests (100%)

---

## Notes

**Tests**: Testing tasks (T111-T116) are optional and marked [P]. Include only if your team practices TDD or spec explicitly requests testing.

**Parallelization**: 47 tasks marked [P] can be executed in parallel if you have multiple developers. Single developer should follow sequential order within each phase.

**MVP Scope**: For fastest time-to-value, implement only Phases 1-5 (US1, US2, US6) first. This delivers core conversational task management. Phases 6-8 add nice-to-have edit/delete capabilities.

**Constitution Compliance**: All tasks align with Phase III constitution principles (stateless agent, MCP integration, conversation persistence, security).
