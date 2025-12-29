# Backend Guidelines

## Stack
- **Framework**: FastAPI 0.95.2
- **ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic v2)
- **Database**: Neon PostgreSQL (production), SQLite (local)
- **Authentication**: Better Auth + JWT
- **Testing**: pytest
- **Migration**: Alembic

## Project Structure
- `app/main.py` - FastAPI app entry point
- `app/models/` - SQLModel database models
- `app/api/` - API route handlers (routers)
- `app/schemas/` - Pydantic request/response schemas
- `app/services/` - Business logic layer
- `app/core/` - Core functionality (auth, config, db)
- `app/db.py` - Database connection
- `alembic/` - Database migrations

## API Conventions
- All routes under `/api/`
- Return JSON responses
- Use Pydantic models for request/response
- Handle errors with HTTPException
- Use `Depends(get_current_user)` for authenticated routes
- Include proper status codes (200, 201, 204, 400, 401, 404, 422, 500)

## Database
- Use SQLModel for all database operations
- Connection string from environment variable: `DATABASE_URL`
- All models inherit from `SQLModel, table=True`
- Use Alembic for all schema changes
- Add `created_at` and `updated_at` timestamps to all models

## Running

### Development
```bash
uvicorn app.main:app --reload --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py
```

## Available Skills

The backend has access to specialized skills from `.claude/skills/` for common development tasks:

### Backend Scaffolding
**Skill**: `backend-scaffolder`

Scaffolds complete FastAPI vertical slices (Model, Schema, Router) with SQLModel, JWT auth, and pytest tests.

**When to use**:
- Implementing the backend for a new feature
- Generating CRUD endpoints
- After creating a feature spec

**What it provides**:
- SQLModel class in `app/models/`
- Pydantic schemas in `app/schemas/`
- FastAPI router in `app/api/` with all CRUD endpoints
- JWT authentication via `Depends(get_current_user)`
- Comprehensive error handling
- Pytest test suite in `tests/`

### CRUD Builder
**Skill**: `crud-builder`

Generates complete CRUD operations for data models.

**When to use**:
- Creating CRUD for a new model
- Adding standard database operations

**What it provides**:
- SQLModel database model with constraints
- Pydantic request/response schemas
- FastAPI router with 5 CRUD endpoints
- JWT authentication and user_id scoping
- Pagination for list endpoints
- Pytest test suite

### FastAPI Endpoint Generator
**Skill**: `fastapi-endpoint-generator`

Generates custom FastAPI endpoints for non-CRUD operations.

**When to use**:
- Creating custom business logic endpoints
- Implementing batch operations
- Building analytics or action endpoints

**What it provides**:
- Custom FastAPI endpoint with proper HTTP method
- Pydantic schemas for validation
- JWT authentication integration
- Error handling with status codes
- OpenAPI/Swagger documentation

### Database Migration Wizard
**Skill**: `db-migration-wizard`

Automates Alembic migrations for schema changes.

**When to use**:
- Adding/modifying database columns
- Changing column types
- Creating new tables
- Handling data migrations

**What it provides**:
- Updates SQLModel models
- Generates Alembic migration: `alembic revision --autogenerate`
- Data conversion SQL if needed
- Migration testing (upgrade/downgrade)
- Data integrity verification

### SQLModel Schema Builder
**Skill**: `sqlmodel-schema-builder`

Builds SQLModel database schemas with relationships and indexes.

**When to use**:
- Designing database tables and relationships
- Implementing data persistence layer
- Adding new models

**What it provides**:
- SQLModel schema design (tables, fields, constraints)
- Pydantic integration (Create/Update/Read schemas)
- Alembic migrations (auto-generation, manual, rollback)
- Relationships (one-to-many, many-to-many)
- Best practices (timestamps, soft deletes, indexes)

### MCP Tool Maker
**Skill**: `mcp-tool-maker`

Creates MCP tools to expose backend functionality to AI agents.

**When to use**:
- Building AI-powered features (Phase III)
- Exposing functions to AI agents
- Creating tools for OpenAI ChatKit integration

**What it provides**:
- MCP server setup with tool registration
- FastAPI router integration for MCP endpoints
- Tool templates with JWT authentication
- OpenAI ChatKit configuration

### Agent Orchestrator
**Skill**: `agent-orchestrator`

Orchestrates AI agent initialization with database context and JWT authentication.

**When to use**:
- Phase III: Building stateless AI assistants
- Setting up agent orchestration
- Implementing conversation management

**What it provides**:
- Database models for conversations and messages
- AgentOrchestrator class with stateless pattern
- FastAPI chat router with REST endpoints
- JWT authentication integration

### Chatkit Integrator
**Skill**: `chatkit-integrator`

Integrates OpenAI Chatkit with database-backed conversation persistence.

**When to use**:
- Phase III: Building AI chat interfaces
- Implementing conversation persistence
- Creating custom Chatkit backend adapter

**What it provides**:
- Complete backend setup (models, schemas, router, agent)
- Stateless agent context loading
- FastAPI chat endpoints (CRUD conversations/messages)
- Implementation guide and testing procedures

### Conversation History Manager
**Skill**: `conversation-history-manager`

Provides conversation history management patterns for database-backed AI chat.

**When to use**:
- Phase III: Managing AI chat conversation state
- Implementing stateless context loading
- Adding cursor-based pagination

**What it provides**:
- 7 core query patterns (context loading, pagination, soft delete, polling, search, metadata, archival)
- Context manager utilities for stateless context loading
- Database schema with performance indexes
- Security patterns (tenant isolation)

### Stateless Agent Enforcer
**Skill**: `stateless-agent-enforcer`

Validates and enforces stateless agent architecture compliance.

**When to use**:
- Phase III: Validating agent implementations
- Before committing agent code
- Code review for agent implementations

**What it provides**:
- Static analysis validator for CI/CD
- Compliance test suite (state isolation, concurrency, restart)
- Code review checklist for PR reviews
- Architecture guide with anti-patterns

### Integration Tester
**Skill**: `integration-tester`

Creates comprehensive integration tests for API endpoints and database operations.

**When to use**:
- Testing API endpoints
- Validating frontend-backend communication
- Testing database operations

**What it provides**:
- Pytest integration tests with TestClient
- Database fixtures with transaction rollback
- Authentication token fixtures
- Happy path and error scenario tests

### Performance Analyzer
**Skill**: `performance-analyzer`

Analyzes application performance to identify bottlenecks.

**When to use**:
- API endpoints have high response times
- Database queries are inefficient
- Before production deployment

**What it provides**:
- API performance analysis (response times, P95/P99 latency)
- Database query performance (slow queries, missing indexes)
- Performance recommendations with optimizations

### Code Reviewer
**Skill**: `code-reviewer`

Performs comprehensive code review with static analysis and security checks.

**When to use**:
- Reviewing code changes
- Before creating pull requests
- Security vulnerability concerns

**What it provides**:
- Multi-tool analysis (ruff, mypy, bandit)
- Best practice validation
- Security vulnerability detection
- Performance anti-pattern identification

### Task Breaker
**Skill**: `task-breaker`

Breaks down large tasks into smaller, manageable subtasks.

**When to use**:
- Complex feature implementation
- Sprint planning requires task breakdown
- Need to estimate effort

**What it provides**:
- Task decomposition strategies
- Task properties (title, description, acceptance criteria, estimates)
- Dependency management and critical path analysis

### Test Builder
**Skill**: `test-builder`

Builds comprehensive test suites including unit tests, integration tests, and E2E tests.

**When to use**:
- Writing tests for new features
- Implementing TDD (Test-Driven Development)
- Increasing test coverage

**What it provides**:
- Backend testing (pytest, fixtures, mocking, TestClient)
- Integration test patterns for FastAPI endpoints
- Coverage reporting and thresholds
- Complete test examples

## Development Workflow

### 1. Feature Implementation
1. Read feature spec from `specs/features/[feature].md`
2. Use `backend-scaffolder` skill to generate boilerplate
3. Implement business logic in services layer
4. Add custom endpoints with `fastapi-endpoint-generator` if needed
5. Write tests with `test-builder` skill
6. Run `pytest` to verify
7. Create database migration with `db-migration-wizard` if schema changes needed

### 2. Database Changes
1. Update SQLModel models in `app/models/`
2. Run `alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Test migration: `alembic upgrade head`
5. Test rollback: `alembic downgrade -1`

### 3. Testing
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_tasks.py::test_create_task
```

### 4. Code Quality
```bash
# Linting
ruff check .

# Type checking
mypy .

# Security scan
bandit -r .

# Format code
ruff format .
```

## Environment Variables

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Authentication
BETTER_AUTH_SECRET=your-secret-key
JWT_SECRET=your-jwt-secret

# AI (Phase III)
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
```

## Common Patterns

### Authenticated Route
```python
from app.core.auth import get_current_user
from app.models.user import User

@router.get("/api/tasks")
async def get_tasks(
    current_user: User = Depends(get_current_user)
):
    return {"tasks": [...]}
```

### Error Handling
```python
from fastapi import HTTPException

if not task:
    raise HTTPException(
        status_code=404,
        detail="Task not found"
    )
```

### Database Session
```python
from app.db import get_session

@router.post("/api/tasks")
async def create_task(
    task: TaskCreate,
    session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_task = Task.from_orm(task, user_id=current_user.id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

## Best Practices

1. **Type Hints**: Add type hints to all functions
2. **Docstrings**: Use Google-style docstrings for public functions
3. **Error Messages**: Return structured error responses
4. **Validation**: Use Pydantic for all request validation
5. **Security**: Never log sensitive data (tokens, passwords)
6. **Testing**: Write tests before or during implementation (TDD)
7. **Migrations**: Always review auto-generated migrations
8. **Performance**: Use selectinload/joinedload to avoid N+1 queries

## Phase-Specific Guidelines

### Phase I: Console App
- No database (use file storage)
- No FastAPI (use argparse/Click)
- Single `main.py` file

### Phase II: Web App
- Use FastAPI + SQLModel
- Modular architecture (models, schemas, routers)
- JWT authentication
- PostgreSQL database

### Phase III: AI Chatbot
- Expose MCP tools for AI agents
- Stateless agent architecture (no in-memory state)
- Database-backed conversation persistence
- OpenAI ChatKit integration

### Phase IV: Microservices
- Docker containerization
- Kubernetes deployment
- Service-specific databases
- Independent deployability

### Phase V: Event-Driven
- Dapr pub/sub for events
- Kafka/Redpanda for event streaming
- Event schema validation
- Idempotent event handlers
