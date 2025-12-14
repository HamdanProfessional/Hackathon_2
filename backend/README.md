# Todo CRUD Backend - FastAPI + AI Agent

REST API backend for the Todo CRUD application with AI-powered chatbot interface. Built with FastAPI, SQLAlchemy, PostgreSQL, and OpenAI Agents SDK.

## Tech Stack

### Core
- **Framework**: FastAPI 0.109+
- **Database ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic 2.5+
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Database**: PostgreSQL 14+ (Neon)

### Phase III: AI Agent Integration
- **AI Model**: OpenAI GPT-4 (via OpenAI SDK >= 1.0.0)
- **Tool Protocol**: Model Context Protocol (MCP SDK >= 1.0.0)
- **Agent Architecture**: Stateless agent with function calling
- **Conversation Storage**: Database-backed persistence

## Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI application instance (v3.0.0)
│   ├── config.py         # Settings and configuration
│   ├── database.py       # Database connection and session
│   ├── models/           # SQLAlchemy ORM models
│   │   ├── user.py       # User model
│   │   ├── task.py       # Task model
│   │   ├── conversation.py    # ⭐ NEW: Conversation model
│   │   └── message.py         # ⭐ NEW: Message model
│   ├── schemas/          # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── chat.py            # ⭐ NEW: Chat request/response
│   │   ├── conversation.py    # ⭐ NEW: Conversation schemas
│   │   └── message.py         # ⭐ NEW: Message schemas
│   ├── crud/             # Database CRUD operations
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── conversation.py    # ⭐ NEW: Conversation CRUD
│   │   └── message.py         # ⭐ NEW: Message CRUD
│   ├── api/              # API route handlers
│   │   ├── deps.py       # Dependencies (get_db, get_current_user)
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── tasks.py      # Task CRUD endpoints
│   │   └── chat.py       # ⭐ NEW: AI chat endpoints
│   ├── mcp/              # ⭐ NEW: MCP tools
│   │   └── tools/
│   │       ├── add_task.py        # Create tasks via NL
│   │       ├── list_tasks.py      # List/filter tasks
│   │       ├── complete_task.py   # Toggle completion
│   │       ├── update_task.py     # Edit task details
│   │       └── delete_task.py     # Delete with confirmation
│   ├── services/         # ⭐ NEW: Business logic services
│   │   └── agent_service.py       # OpenAI agent orchestration
│   └── utils/            # Utilities (security, exceptions)
├── alembic/              # Database migrations
│   └── versions/
│       └── 001_add_conversations_and_messages.py  # ⭐ NEW
├── tests/                # Pytest tests
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── README.md             # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Phase II: Core Backend
DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000

# Phase III: AI Agent Integration ⭐ NEW
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
MAX_TOKENS_PER_DAY=50000
```

#### Getting a Neon Database URL:

1. Sign up at https://neon.tech
2. Create a new project
3. Copy the connection string
4. Format: `postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require`

#### Getting an OpenAI API Key:

1. Sign up at https://platform.openai.com
2. Navigate to API Keys section
3. Create new secret key
4. Copy the key (starts with `sk-`)
5. Add to `.env` as `OPENAI_API_KEY`

**Note**: GPT-4 access may require account upgrade. For testing, you can use `gpt-3.5-turbo` instead.

### 3. Initialize Database

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Run migrations to create tables
alembic upgrade head
```

### 4. Run the Server

```bash
# Development (with auto-reload)
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server will be available at http://localhost:8000

## API Endpoints

### Authentication

- `POST /api/auth/register` - Create new user account
  - Body: `{"email": "user@example.com", "password": "password123"}`
  - Returns: `{"access_token": "...", "token_type": "bearer"}`

- `POST /api/auth/login` - Login and get JWT token
  - Body: `{"email": "user@example.com", "password": "password123"}`
  - Returns: `{"access_token": "...", "token_type": "bearer"}`

### Tasks (Authentication Required)

All task endpoints require the `Authorization: Bearer <token>` header.

- `POST /api/tasks` - Create new task
  - Body: `{"title": "Task title", "description": "Optional description"}`

- `GET /api/tasks` - Get all tasks for current user

- `GET /api/tasks/{id}` - Get single task by ID

- `PUT /api/tasks/{id}` - Update task
  - Body: `{"title": "New title", "description": "New description"}`

- `PATCH /api/tasks/{id}/complete` - Toggle task completion status

- `DELETE /api/tasks/{id}` - Delete task

### ⭐ Chat (Phase III - Authentication Required)

AI-powered task management through natural language conversation.

- `POST /api/chat` - Send message to AI assistant
  - Body: `{"message": "Add buy groceries to my list", "conversation_id": 1}`
  - Returns: `{"conversation_id": 1, "response": "I've added 'Buy groceries' to your task list.", "tool_calls": [...]}`
  - Note: `conversation_id` is optional for first message in new conversation

- `GET /api/chat/conversations` - List all conversations for current user
  - Returns: `[{"id": 1, "created_at": "...", "updated_at": "..."}]`

- `GET /api/chat/conversations/{id}/messages` - Get conversation history
  - Returns: `[{"role": "user", "content": "Add buy milk"}, {"role": "assistant", "content": "I've added..."}]`

#### Natural Language Commands Supported

- **Create**: "Add buy milk", "Remind me to call mom", "I need to finish the report"
- **List**: "Show my tasks", "What's on my list?", "Show completed tasks"
- **Complete**: "I finished buying groceries", "Mark task 5 as done"
- **Update**: "Change task 3 to buy organic milk", "Add description to task 2"
- **Delete**: "Delete task 5" (agent will ask for confirmation first)

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Migrations

### Create a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration in alembic/versions/

# Apply the migration
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_auth.py
```

### Run with Coverage

```bash
pytest --cov=app tests/
```

## Manual Testing with curl

### Register a User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Create a Task

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token-here>" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}'
```

### Get All Tasks

```bash
curl -X GET "http://localhost:8000/api/tasks" \
  -H "Authorization: Bearer <your-token-here>"
```

## Deployment

### Railway

1. Create account at https://railway.app
2. Create new project
3. Add PostgreSQL database
4. Deploy from GitHub repository
5. Set environment variables in Railway dashboard
6. Run migrations: `railway run alembic upgrade head`

### Render

1. Create account at https://render.com
2. Create new Web Service
3. Connect GitHub repository
4. Set build command: `pip install -r backend/requirements.txt`
5. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add PostgreSQL database
7. Set environment variables
8. Deploy and run migrations

### Fly.io

1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Create `fly.toml` configuration
3. Deploy: `fly deploy`
4. Add PostgreSQL: `fly postgres create`
5. Set environment variables: `fly secrets set KEY=value`

## Troubleshooting

### Database Connection Errors

- Verify DATABASE_URL is correct
- Check that Neon project is active
- Ensure SSL mode is set: `?sslmode=require`

### Migration Errors

- Check Alembic configuration in `alembic/env.py`
- Verify models are imported correctly
- Review migration file before applying

### CORS Errors

- Verify CORS_ORIGINS includes your frontend URL
- Check that middleware is configured in `app/main.py`

## Security Notes

- Never commit `.env` file
- Use strong JWT_SECRET_KEY (generate with `openssl rand -hex 32`)
- Enable HTTPS in production
- Restrict CORS_ORIGINS to your frontend domain
- Use environment-specific configurations

## Development Tips

- Use `--reload` flag for auto-reload during development
- Check FastAPI docs at `/docs` for interactive API testing
- Use pytest fixtures for database setup/teardown
- Review SQLAlchemy queries with `echo=True` in database.py

## ⭐ Phase III: AI Agent Architecture

### MCP Tools

The backend implements 5 MCP (Model Context Protocol) tools that the AI agent can call:

1. **add_task** (`app/mcp/tools/add_task.py`)
   - Creates new tasks from natural language
   - Validates title length, sanitizes input
   - Auto-injects user_id for security

2. **list_tasks** (`app/mcp/tools/list_tasks.py`)
   - Lists tasks with filtering (all/pending/completed)
   - Returns formatted task data with IDs
   - Respects user isolation

3. **complete_task** (`app/mcp/tools/complete_task.py`)
   - Toggles task completion status
   - Validates ownership before updating
   - Returns updated status

4. **update_task** (`app/mcp/tools/update_task.py`)
   - Updates task title and/or description
   - Requires at least one field
   - Validates ownership

5. **delete_task** (`app/mcp/tools/delete_task.py`)
   - Permanently deletes tasks
   - Requires explicit user confirmation
   - Validates ownership

### Agent Service

**File**: `app/services/agent_service.py`

- **Stateless Design**: No in-memory sessions, all state in database
- **OpenAI Integration**: Uses function calling with GPT-4
- **System Prompt**: Defines agent behavior and tool usage patterns
- **Tool Execution**: Injects user_id into all tool calls for security
- **Response Formatting**: Converts tool results into conversational responses

### Conversation Persistence

- **Conversations**: Stored in `conversations` table with user_id, timestamps
- **Messages**: Stored in `messages` table with role (user/assistant) and content
- **History Loading**: Last 50 messages loaded on each request for context
- **Auto-update**: Trigger function updates conversation.updated_at on new messages

### Security Features

- **User ID Injection**: Never accepted from client, always from JWT auth
- **Ownership Validation**: All CRUD operations validate user owns resource
- **Confirmation Flows**: Destructive actions (delete) require explicit confirmation
- **Input Validation**: Length limits, type checking, sanitization
- **Token Management**: Configurable daily token budget (MAX_TOKENS_PER_DAY)

### Agent Example Usage

```python
from app.services.agent_service import AgentService

# Initialize agent for authenticated user
agent = AgentService(user_id=current_user.id)

# Process user message
result = await agent.process_message(
    message_history=[
        {"role": "user", "content": "Add buy milk"},
        {"role": "assistant", "content": "I've added 'Buy milk' to your list."}
    ],
    user_message="Show me my tasks"
)

# result = {
#     "response": "Here are your tasks:\n⬜ Buy milk\n(1 task)",
#     "tool_calls": [{"tool": "list_tasks", "parameters": {"status": "all"}, "result": {...}}]
# }
```
