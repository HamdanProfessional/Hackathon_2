# Task Implementation Breakdown: AI-Powered Todo Chatbot

**Feature**: 003-ai-chatbot
**Created**: 2025-12-17
**Status**: COMPLETED
**Total Tasks**: 54 (including migration)
**Implementation Phases**: 7 + Migration

## Dependencies

**Phase Completion Order**:
1. Phase 1: Setup (Infrastructure)
2. Phase 2: Foundational (Core Models & Services)
3. Phase 3: US1 + US6 (Task Creation & Conversation Persistence) - MVP
4. Phase 4: US2 (Task Listing)
5. Phase 5: US3 (Task Completion)
6. Phase 6: US4 (Task Updates)
7. Phase 7: US5 (Task Deletion)

**Parallel Execution**:
- [P] tasks within each phase can be executed in parallel by different developers
- Each User Story phase is independently testable after completion
- US6 (Conversation Persistence) is implemented in Phase 3 as it's foundational for chat functionality

## Phase 1: Setup (Infrastructure)

**Goal**: Install dependencies and configure development environment

### Tasks
- [ ] T001 Install Python dependencies: openai, mcp in backend/requirements.txt
- [ ] T002 [P] Install frontend dependency: @openai/chatkit in frontend/package.json
- [ ] T003 Add OpenAI API key configuration to backend/.env.example
- [ ] T004 [P] Create AI module directory structure: backend/app/ai/
- [ ] T005 Verify MCP SDK installation and basic connectivity

**Definition of Done**:
- All dependencies installed without errors
- Environment variables documented
- Basic MCP connection test passes

---

## Phase 2: Foundational (Data Layer & Core Services)

**Goal**: Create database models and migration for conversation persistence

### Tasks
- [X] T006 Create Conversation model in backend/app/models/conversation.py
- [X] T007 [P] Create Message model in backend/app/models/message.py
- [X] T008 Add Conversation and Message to backend/app/models/__init__.py
- [X] T009 Generate Alembic migration for new tables
- [X] T010 Run database migration and verify tables created
- [X] T011 Create ConversationService in backend/app/services/conversation_service.py
- [X] T012 [P] Create MessageService in backend/app/services/message_service.py

**Definition of Done**:
- Models created with proper relationships and indexes
- Migration applied successfully
- Basic CRUD services operational

---

## Phase 3: US1 + US6 - Task Creation & Conversation Persistence (MVP)

**Story Goal**: Users can create tasks through natural language chat with conversation persistence

**Independent Test**:
1. User opens chat interface
2. Types "Add buy milk to my todo list"
3. System creates task with title "Buy milk"
4. System confirms creation
5. Refresh browser - conversation history persists

### Tasks
- [X] T013 [US1] Create MCP tools wrapper in backend/app/ai/tools.py (add_task only)
- [X] T014 [P] [US6] Create OpenAI Agent service in backend/app/ai/agent.py
- [X] T015 [US1] Implement tool call loop in agent service
- [X] T016 [P] [US6] Add conversation history loading to agent
- [X] T017 [US1] Create chat endpoint in backend/app/api/chat.py
- [X] T018 [P] [US6] Implement conversation persistence in chat endpoint
- [X] T019 [US1] Add user authentication to chat endpoint
- [X] T020 [P] [US6] Add message saving after agent response
- [X] T021 [US1] Configure chat state management in frontend
- [X] T022 [P] [US6] Create ChatWidget component in frontend/components/chat/chat-widget.tsx
- [X] T023 [US1] Connect to POST /api/chat endpoint
- [X] T024 [P] [US6] Implement conversation history loading in UI
- [X] T025 [US1] Style chat widget to match Nebula 2025 theme
- [X] T026 [P] [US6] Add chat widget to dashboard layout

**Definition of Done**:
- User can create tasks via natural language
- Tasks appear in main todo list
- Conversation history persists across refreshes
- UI is responsive and themed

---

## Phase 4: US2 - Conversational Task Listing

**Story Goal**: Users can ask to see their tasks using natural language queries

**Independent Test**:
1. User creates 5 tasks via chat or web UI
2. User types "What's on my todo list?"
3. System displays all 5 pending tasks in chat
4. User asks "Show me completed tasks"
5. System shows only completed tasks

### Tasks
- [X] T027 [US2] Add list_tasks MCP tool to backend/app/ai/tools.py
- [X] T028 [P] [US2] Implement task status filtering in list tool
- [X] T029 [US2] Add date filtering for "today's tasks" queries
- [X] T030 [P] [US2] Update agent prompt to handle listing requests
- [X] T031 [US2] Format task lists for chat display
- [X] T032 [P] [US2] Handle empty task list responses

**Definition of Done**:
- System responds to various listing phrasings
- Filters work correctly (pending, completed, today)
- Empty lists show friendly messages

---

## Phase 5: US3 - Natural Language Task Completion

**Story Goal**: Users can mark tasks as complete by referring to them naturally

**Independent Test**:
1. User has task "Buy groceries"
2. User types "I finished buying groceries"
3. System marks task as complete
4. System confirms completion

### Tasks
- [X] T033 [US3] Add complete_task MCP tool to backend/app/ai/tools.py
- [X] T034 [P] [US3] Implement fuzzy task matching in completion tool
- [X] T035 [US3] Add task ID support for completion
- [X] T036 [P] [US3] Update agent to handle completion intent
- [X] T037 [US3] Add confirmation messages for completion

**Definition of Done**:
- Tasks can be completed by title or ID
- System handles ambiguous references
- Clear confirmations provided

---

## Phase 6: US4 - Conversational Task Updates

**Story Goal**: Users can modify existing tasks through natural language

**Independent Test**:
1. User has task "Buy milk"
2. User types "Change buy milk to buy groceries"
3. System updates task title
4. System confirms the change

### Tasks
- [X] T038 [US4] Add update_task MCP tool to backend/app/ai/tools.py
- [X] T039 [P] [US4] Implement task field detection (title, description)
- [X] T040 [US4] Add clarification prompts for ambiguous updates
- [X] T041 [P] [US4] Update agent to handle update requests
- [X] T042 [US4] Add update confirmation messages

**Definition of Done**:
- Task titles and descriptions can be updated
- System asks for clarification when needed
- Changes reflected in main UI

---

## Phase 7: US5 - Natural Language Task Deletion

**Story Goal**: Users can remove tasks by requesting deletion with confirmation

**Independent Test**:
1. User has task "Old meeting notes"
2. User types "Delete old meeting notes task"
3. System asks for confirmation
4. User responds "Yes"
5. Task is deleted and confirmed

### Tasks
- [X] T043 [US5] Add delete_task MCP tool to backend/app/ai/tools.py
- [X] T044 [P] [US5] Implement confirmation flow in agent
- [X] T045 [US5] Add task identification for deletion
- [X] T046 [P] [US5] Handle cancellation of deletion
- [X] T047 [US5] Update agent to handle deletion requests
- [X] T048 [P] [US5] Add deletion confirmation messages

**Definition of Done**:
- Tasks deleted only after explicit confirmation
- Clear cancellation option provided
- Deletion reflected in main UI

---

## Final Phase: Polish & Cross-Cutting Concerns

**Goal**: Ensure robustness, performance, and user experience

### Tasks
- [X] T049 Add error handling for OpenAI API failures
- [X] T050 [P] Implement rate limiting on chat endpoint
- [X] T051 Add loading indicators during AI processing
- [X] T052 [P] Add markdown rendering for AI responses
- [X] T053 Implement conversation pagination for long histories

**Definition of Done**:
- Graceful error handling throughout
- Performance meets requirements (<3s response)
- UI is polished and professional

---

## Additional Task: Gemini Migration

### Task
- [X] T054 [MIGRATION] Refactor AgentService from OpenAI to Google Gemini 2.5 Flash

**Description**:
- Updated backend configuration to use Gemini API key and base URL
- Migrated from OpenAI client to AsyncOpenAI with Gemini's OpenAI-compatible endpoint
- Updated model from gemini-2.0-flash-exp to gemini-2.5-flash
- All existing MCP tools and functionality preserved

## Implementation Strategy

### MVP Delivery (Phase 3 Only)
For fastest delivery, implement only Phase 3 which includes:
- Core task creation via natural language (US1)
- Conversation persistence (US6)
- Basic chat interface

This provides immediate value while foundation for other stories is in place.

### Incremental Delivery
Each subsequent phase can be delivered independently:
- Phase 4 adds task viewing capabilities
- Phase 5 adds task completion
- Phase 6 adds task updates
- Phase 7 adds task deletion

### Parallel Development Opportunities
- Frontend ChatWidget styling can proceed while backend tools are built
- MCP tools for different operations can be developed in parallel
- Error handling and polish tasks can be done alongside feature development

## Testing Strategy

Each User Story phase includes an independent test that verifies:
1. The core functionality works end-to-end
2. Integration with existing Phase II features
3. Conversation persistence across browser sessions

Tests should be run after each phase completion before proceeding to the next phase.
