Here is the **fully detailed, comprehensive `requirements.md`** covering Phases I, II, and III.

I have included **every technical table, endpoint definition, MCP tool parameter, and architecture constraint** from your original text, updated with the mandatory **Gemini 2.5 Flash** and **Better Auth JWT** pivots.

```markdown
# Hackathon II: The Evolution of Todo (Phases I-III)
## Mastering Spec-Driven Development, Reusable Intelligence & Cloud-Native AI

The future of software development is AI-native and spec-driven. As AI agents like Claude Code become more powerful, the role of the engineer shifts from "syntax writer" to "system architect."

In this hackathon, you will master the art of building applications iteratively—starting from a simple console app and evolving it into a fully-featured AI chatbot. This journey will teach you the **Nine Pillars of AI-Driven Development**, **Claude Code**, **Spec-Driven Development**, and **Agentic AI** technologies.

---

## 🛠 Core Constraints & Rules

1.  **Spec-Driven Implementation:** You are **strictly required** to use Spec-Driven Development. You must write a Markdown Constitution and Spec for every feature, and use Claude Code to generate the implementation.
2.  **No Manual Coding:** You cannot write the code manually. You must refine the Spec until Claude Code generates the correct output.
3.  **Agentic Workflow:** Follow the cycle: **Specify (`.specify`) → Plan (`.plan`) → Tasks (`.tasks`) → Implement**.
4.  **Integrated AI Chatbot:** In Phase III, you must implement a conversational interface using **OpenAI Chatkit**, **OpenAI Agents SDK** (orchestrating **Gemini 2.5 Flash**), and **Official MCP SDK**.

---

## 🏗 Project Architecture & Tech Stack

| Component | Technology |
| :--- | :--- |
| **Project Manager** | `uv` (Universal Python Package Manager) |
| **Frontend** | Next.js 16+ (App Router), Tailwind CSS |
| **Backend** | Python FastAPI |
| **Database** | Neon Serverless PostgreSQL |
| **ORM** | SQLModel (Pydantic v2 compatible) |
| **Authentication** | Better Auth (Frontend) + JWT Verification (Backend) |
| **AI Runtime** | OpenAI Agents SDK (Python) |
| **AI Model** | **Google Gemini 2.5 Flash** (via OpenAI Compatibility) |
| **Tooling** | Official MCP (Model Context Protocol) SDK |
| **UI Framework** | OpenAI ChatKit |

---

## 📂 Phase I: In-Memory Python Console App

**Objective:** Build a command-line todo application that stores tasks in memory, but uses production-ready **SQLModel** classes to ensure forward compatibility.

### Functional Requirements (Basic Level)
*   **Add Task:** Create new todo items with Title (required) and Description (optional).
*   **Delete Task:** Remove tasks by ID.
*   **Update Task:** Modify existing task details.
*   **View Task List:** Display all tasks (use `Rich` library for tables).
*   **Mark as Complete:** Toggle task completion status.

### Deliverables
*   **Repo Structure:** `src/` containing `main.py`, `models/`, `controllers/`.
*   **Constitution:** `specs/constitution.md` defining the Spec-Driven rules.
*   **Working App:** Must demonstrate all 5 CRUD operations via CLI.

---

## 🌐 Phase II: Full-Stack Web Application

**Objective:** Transform the console app into a multi-user web application with persistent storage in Neon DB and secure authentication.

### 1. Database Schema
You must use **SQLModel** to define these tables in Postgres:

| Table | Fields | Description |
| :--- | :--- | :--- |
| **User** | `id` (str, PK), `email` (unique), `name`, `created_at` | Managed by Better Auth |
| **Task** | `id` (int, PK), `user_id` (FK), `title`, `description`, `completed`, `priority`, `due_date`, `tags`, `created_at`, `updated_at` | Todo items (User isolated) |

### 2. Authentication Strategy (Better Auth + JWT)
*   **Frontend:** Better Auth handles user login (Email/Pass or Social).
*   **Token Issue:** Better Auth must be configured to issue a **JWT** signed with `BETTER_AUTH_SECRET`.
*   **Backend Verification:** FastAPI middleware must verify the JWT on every request using the same secret.
*   **User Isolation:** The backend must extract `user_id` from the token and filter all database queries to strictly return that user's data.

### 3. REST API Endpoints
All endpoints must be protected by the JWT Middleware.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/{user_id}/tasks` | List all tasks (Filter by status, priority) |
| `POST` | `/api/{user_id}/tasks` | Create a new task |
| `GET` | `/api/{user_id}/tasks/{id}` | Get specific task details |
| `PUT` | `/api/{user_id}/tasks/{id}` | Update task details |
| `DELETE` | `/api/{user_id}/tasks/{id}` | Delete a task |
| `PATCH` | `/api/{user_id}/tasks/{id}/complete` | Toggle completion status |

---

## 🤖 Phase III: AI-Powered Todo Chatbot

**Objective:** Create a natural language interface where an AI Agent actively manages the Todo list using **MCP Tools**.

### 1. AI Implementation Strategy (Gemini Pivot)
You must use the **OpenAI Agents SDK** but configure it to use **Google Gemini 2.5 Flash**.

**Required Code Pattern:**
```python
from openai import AsyncOpenAI
from agents import Agent, Runner, set_default_openai_client, OpenAIChatCompletionsModel
import os

# 1. Configure Google Client
gemini_client = AsyncOpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 2. Set as Default
set_default_openai_client(gemini_client)

# 3. Model Adapter (CRITICAL: Use ChatCompletionsModel, NOT Responses)
gemini_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=gemini_client
)
```

### 2. Chat API & Stateless Architecture
The backend must be **Stateless**. State is persisted in the DB on every turn.

**Database Models for Chat:**
| Model | Fields | Description |
| :--- | :--- | :--- |
| **Conversation** | `user_id`, `id`, `created_at`, `updated_at` | Chat session metadata |
| **Message** | `user_id`, `id`, `conversation_id`, `role` (user/assistant), `content`, `created_at` | Chat history logs |

**API Endpoint:**
*   **POST** `/api/{user_id}/chat`
*   **Request:** `{"conversation_id": 123 (opt), "message": "Buy milk"}`
*   **Response:** `{"conversation_id": 123, "response": "Task added.", "tool_calls": [...]}`

**Stateless Flow Cycle:**
1.  Receive message → 2. Fetch history from DB → 3. Build context → 4. Save User Message → 5. Run Agent (Gemini) → 6. Agent calls MCP Tools → 7. Save Assistant Response → 8. Return to Client.

### 3. MCP Tools Specification (Model Context Protocol)
The MCP server must expose these exact tools. The Agent calls these, not the database directly.

**Tool: add_task**
*   **Purpose:** Create a new task.
*   **Parameters:** `user_id` (str, req), `title` (str, req), `description` (str, opt).
*   **Returns:** `task_id`, `status`, `title`.
*   **Example Input:** `{"user_id": "ziakhan", "title": "Buy groceries", "description": "Milk"}`

**Tool: list_tasks**
*   **Purpose:** Retrieve tasks.
*   **Parameters:** `user_id` (str, req), `status` (str, opt: "all"|"pending"|"completed").
*   **Returns:** Array of task objects.

**Tool: complete_task**
*   **Purpose:** Mark as complete.
*   **Parameters:** `user_id` (str, req), `task_id` (int, req).
*   **Returns:** `task_id`, `status`.

**Tool: delete_task**
*   **Purpose:** Remove a task.
*   **Parameters:** `user_id` (str, req), `task_id` (int, req).
*   **Returns:** `task_id`, `status`.

**Tool: update_task**
*   **Purpose:** Modify details.
*   **Parameters:** `user_id` (str, req), `task_id` (int, req), `title` (str, opt), `description` (str, opt).
*   **Returns:** `task_id`, `status`.

### 4. Agent Behavior Specification
The AI must be prompted to handle these natural language intents:

| User Says | Agent Should |
| :--- | :--- |
| "Add a task to buy groceries" | Call `add_task` with title "Buy groceries" |
| "Show me all my tasks" | Call `list_tasks` with status "all" |
| "What's pending?" | Call `list_tasks` with status "pending" |
| "Mark task 3 as complete" | Call `complete_task` with `task_id` 3 |
| "Delete the meeting task" | Call `list_tasks` to find ID, then `delete_task` |
| "Change task 1 to 'Call mom'" | Call `update_task` with new title |

### 5. Advanced & Bonus Features
*   **Recurring Tasks:** Logic to handle "Remind me every Monday" (Logic in Agent or Backend).
*   **Due Dates:** Set specific `due_date` fields via the `add_task` tool.
*   **Multi-language (Urdu):** The chatbot must support Urdu input/output (e.g., "Mera kaam likh lo").
*   **Voice Commands:** Use browser Speech-to-Text to populate the ChatKit input field.
*   **Blueprints:** The agent should have a skill to output Deployment YAMLs if asked.

---

## 🗂 Monorepo Structure (Spec-Kit Plus)

You must use this specific Monorepo structure for seamless Spec-Driven Development:

```text
new_structure/
├── .specify/                         # Spec-Kit Engine
│   ├── memory/constitution.md        # Global Context (The "Brain")
│   ├── plans/                        # Implementation Plans
│   └── tasks/                        # Atomic Task Files
├── .claude/                          # AI Config
│   ├── agents/                       # Persona Files (e.g., backend-specialist.md)
│   └── skills/                       # Core Logic (e.g., Backend-Engineer-Core)
├── specs/                            # Specifications
│   ├── features/                     # Feature Specs (Phase I-III)
│   ├── api/                          # REST & MCP Specs
│   └── database/                     # Schema Specs
├── src/                              # Phase I Python Code
├── frontend/                         # Phase II+ Next.js App
├── backend/                          # Phase II+ FastAPI App
├── CLAUDE.md                         # Entry point linking to Constitution
└── requirements.md                   # This file
```

---

## 🚀 Execution Workflow

1.  **Read:** All Agents must read `@.specify/memory/constitution.md` first.
2.  **Specify:** Use the **Spec-Architect** to create detailed specs in `specs/`.
3.  **Plan:** Create a step-by-step plan in `.specify/plans/`.
4.  **Task:** Break the plan into files in `.specify/tasks/`.
5.  **Build:** Use **Backend/Frontend Agents** to implement the code.
6.  **Verify:** Run `uv run` or `npm run dev` to test against the requirements.
```