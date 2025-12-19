---
id: 008
title: "ai chatbot specification"
stage: spec
date: 2025-12-17
surface: agent
model: claude-3-opus-20240229
feature: 003-ai-chatbot
branch: main
user: User
command: /sp.specify Phase III: AI-Powered Todo Chatbot
labels: ["spec", "ai", "chatbot", "mcp", "openai", "phase3"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - AGENTS.md
  - specs/003-ai-chatbot/spec.md
  - specs/003-ai-chatbot/checklists/requirements.md
tests:
  - Constitution updated to Phase III
  - Specification exists with all required sections
  - Checklist shows all validation items passed
---

## Prompt

Phase III: AI-Powered Todo Chatbot

CONTEXT:
Phase II is complete. We are now evolving the application into an AI-native system using the **Agentic Dev Stack**.
We need to integrate the **OpenAI Agents SDK**, **Official MCP SDK**, and **OpenAI ChatKit**.

INSTRUCTIONS:

1. **Update Constitution (`AGENTS.md`)**:
   - Bump Version to **3.0.0**.
   - Mark Phase II as `✅ COMPLETED`.
   - Mark Phase III as `⚙️ IN PROGRESS`.
   - **Adme | Parameters | Description |
|-----------|------------|-------------|
| `add_task` | `title`, `description` (opt), `priority` (opt), `due_date` (opt) | Creates a new task. |
| `list_tasks` | `status` (opt: "all", "pending", "completed"), `priority` (opt), `search` (opt) | Lists tasks based on filters. |
| `update_task` | `task_id`, `title` (opt), `status` (opt) | Updates an existing task. |
| `delete_task` | `task_id` | Deletes a task. |
| `complete_task` | `task_id` | Marks a task as complete. |

## 5. API Endpoint
- **POST** `/api/chat` (Protected by JWT)
  - **Input**: `{ "message": "string", "conversation_id": "int (optional)" }`
  - **Logic**:
    1. Verify User.
    2. Load Conversation History (if ID provided) or Create New.
    3. Append User Message to DB.
    4. Run OpenAI Agent with MCP Tools.
    5. Append Assistant Response to DB.
    6. Return Response.

## 6. Frontend (ChatKit)
- Integrate **OpenAI ChatKit** into the Dashboard.
- **UI**: A collapsible "AI Assistant" sidebar or a floating chat widget.
- **Features**:
  - Real-time streaming of AI responses.
  - Markdown rendering (for lists/bold text).
  - Optimistic UI updates (if the AI adds a task, the main list should refresh).

## 7. Acceptance Criteria
- [ ] Users can add/edit/delete tasks using natural language.
- [ ] "Show me my high priority tasks" filters the list correctly.
- [ ] Conversation history persists across page reloads.
- [ ] The Agent cannot access tasks belonging to other users.
- [ ] UI displays a "Thinking..." state while the Agent is working.

---

ACTION:
Update the constitution and generate the spec file now.

## Response snapshot

Successfully updated the constitution for Phase III and validated the existing AI chatbot specification.

### Constitution Updates:
- Updated AGENTS.md to version 3.0.0
- Marked Phase II as ✅ COMPLETED
- Marked Phase III as ⚙️ IN PROGRESS
- Updated current phase description to reflect AI-native system

### Specification Status:
- The specification file already exists at specs/003-ai-chatbot/spec.md
- It's comprehensive with 6 user stories, 32 functional requirements, and 12 success criteria
- Added specific requirements for MCP tools, OpenAI Agents SDK, ChatKit, and API endpoint structure
- All validation checklist items show as PASSED

## Outcome

- ✅ Impact: Successfully established Phase III foundation with updated constitution and validated specification
- 🧪 Tests: Specification validation complete with all checklist items passed
- 📁 Files: Updated AGENTS.md, enhanced spec.md with MCP and OpenAI details
- 🔁 Next prompts: Ready to proceed with `/sp.plan` for implementation architecture
- 🧠 Reflection: The existing specification was already comprehensive and well-structured

## Evaluation notes (flywheel)

- Failure modes observed: None - specification already met all quality criteria
- Graders run and results (PASS/FAIL): PASS - All validation items passed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A