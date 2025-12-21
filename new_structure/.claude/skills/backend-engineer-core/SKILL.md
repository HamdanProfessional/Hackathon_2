---
name: backend-engineer-core
description: Comprehensive backend development for Python/FastAPI/SQLModel stack. Handles API endpoint generation, database schema design, migrations, CRUD operations, and CORS configuration. Manages the complete backend evolution from console app to full-stack web application to AI-powered chatbot. Use for all Python backend development across Phases I-III.
---

# Backend Engineer Core

## Quick Start

```python
# Scaffold complete backend
from backend_engineer_core import BackendScaffold

scaffold = BackendScaffold(
    project_name="todo-api",
    database_url="postgresql://...",
    features=["auth", "crud", "mcp-tools"]
)

scaffold.generate()

# Output:
# - FastAPI application structure
# - SQLModel definitions
# - CRUD endpoints
# - Database migrations
# - MCP tool implementations
```

## Core Capabilities

### 1. FastAPI Scaffolding
```python
# Auto-generate complete FastAPI app
app = FastAPIBuilder(
    title="Todo API",
    version="1.0.0",
    features=["auth", "tasks", "chat"]
)

# Generated structure:
# - main.py (FastAPI app)
# - routers/ (endpoint modules)
# - models/ (SQLModel definitions)
# - schemas/ (Pydantic models)
# - services/ (business logic)
# - database.py (DB setup)
```

### 2. SQLModel Schema Design
```python
# Define models with relationships
class TaskBase(SQLModel):
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default="")
    completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
```

### 3. CRUD Endpoint Generation
```python
# Auto-generate full CRUD API
@router.post("/tasks", response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Create a new task for authenticated user."""
    db_task = Task.from_orm(task, update={"user_id": current_user})
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

## Phase Detection & Context Awareness

### Phase Detection Logic
```python
import os
from pathlib import Path
from typing import Tuple, Optional

class ProjectPhaseDetector:
    """Automatically detects the current project phase and structure."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def detect_phase(self) -> Tuple[int, str]:
        """
        Detects the current project phase.

        Returns:
            Tuple[int, str]: (phase_number, phase_description)
        """
        # Check for Phase I structure
        if (self.project_root / "src" / "main.py").exists():
            return 1, "Console Application (Phase I)"

        # Check for Phase II structure
        if (self.project_root / "backend" / "main.py").exists():
            return 2, "Full Stack Web Application (Phase II)"

        # Check for Phase III structure (AI components)
        if (self.project_root / "backend" / "app" / "ai").exists():
            return 3, "AI Chatbot Application (Phase III)"

        # Default assumption
        return 1, "Console Application (Phase I - Default)"

    def get_server_command(self) -> Tuple[str, str]:
        """
        Gets the appropriate server command for the current phase.

        Returns:
            Tuple[str, str]: (command, description)
        """
        phase, description = self.detect_phase()

        if phase == 1:
            # Phase I: Console app
            return "uv run src/main.py", "Running console application"
        elif phase == 2:
            # Phase II: FastAPI web server
            return "uvicorn main:app --reload", "Starting FastAPI development server"
        elif phase == 3:
            # Phase III: Full stack with AI
            return "uvicorn main:app --reload", "Starting AI-powered application server"

        # Fallback
        return "uv run src/main.py", "Running console application (fallback)"

    def get_project_structure(self) -> dict:
        """Returns the detected project structure."""
        phase, description = self.detect_phase()

        if phase == 1:
            return {
                "phase": phase,
                "description": description,
                "entry_point": "src/main.py",
                "structure": {
                    "src": "Source code directory",
                    "requirements.txt": "Python dependencies",
                    "README.md": "Project documentation"
                }
            }
        elif phase >= 2:
            return {
                "phase": phase,
                "description": description,
                "entry_point": "backend/main.py",
                "structure": {
                    "backend": "FastAPI application",
                    "frontend": "Next.js frontend (if exists)",
                    "alembic": "Database migrations",
                    "tests": "Test suite"
                }
            }

# Usage
detector = ProjectPhaseDetector()
phase, desc = detector.detect_phase()
command, cmd_desc = detector.get_server_command()

print(f"Detected: {desc}")
print(f"Command: {command}")
```

### Context-Aware Server Runner
```python
import subprocess
import sys
from pathlib import Path

class ContextAwareServerRunner:
    """Runs the appropriate server based on project structure."""

    def __init__(self, project_root: str = "."):
        self.detector = ProjectPhaseDetector(project_root)
        self.project_root = Path(project_root)

    def run_server(self, args: Optional[list] = None) -> None:
        """
        Runs the appropriate server command for the current phase.

        Args:
            args: Additional arguments to pass to the server command
        """
        phase, description = self.detector.detect_phase()
        command, cmd_desc = self.detector.get_server_command()

        print(f"🚀 {cmd_desc}")
        print(f"📁 Project Phase: {description}")
        print(f"⚡ Command: {command}")

        # Prepare full command
        full_command = command.split()
        if args:
            full_command.extend(args)

        # Change to project root if needed
        original_cwd = Path.cwd()
        if str(self.project_root) != str(original_cwd):
            os.chdir(self.project_root)
            print(f"📂 Changed directory to: {self.project_root}")

        try:
            # Run the command
            subprocess.run(full_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Server failed to start: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped by user")
        finally:
            # Restore original directory
            if str(self.project_root) != str(original_cwd):
                os.chdir(original_cwd)

# Command line interface
if __name__ == "__main__":
    runner = ContextAwareServerRunner()

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run Todo Evolution application")
    parser.add_argument("--port", "-p", type=int, help="Port to run server on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    args = parser.parse_args()

    # Prepare server arguments
    server_args = []
    if args.port:
        server_args.extend(["--port", str(args.port)])
    if args.host != "localhost":
        server_args.extend(["--host", args.host])

    runner.run_server(server_args)
```

## Phase Evolution Support

### Phase I: Console Backend (In-Memory)
```python
# Simple in-memory task manager
class TaskManager:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1

    def create_task(self, title: str, description: str = None):
        # In-memory implementation
```

### Phase II: Web Backend (FastAPI + SQLModel)
```python
# Full-featured API with database
class TaskService:
    def __init__(self, session: Session):
        self.session = session

    async def create_task(self, user_id: str, task_data: TaskCreate):
        # Database implementation with SQLModel
```

### Phase III: AI Backend (MCP Tools)
```python
# MCP server for AI integration
@app.call_tool()
async def add_task(arguments: dict):
    """MCP tool for task creation."""
    return await TaskService.create_task(
        user_id=arguments["user_id"],
        task_data=TaskCreate(**arguments)
    )
```

## API Endpoint Patterns

### RESTful CRUD Operations
```python
# Standard CRUD endpoints
@router.get("/tasks")                    # List
@router.post("/tasks")                   # Create
@router.get("/tasks/{id}")               # Read
@router.put("/tasks/{id}")               # Update
@router.delete("/tasks/{id}")            # Delete
@router.patch("/tasks/{id}/complete")    # Custom action
```

### Authentication Middleware
```python
# JWT authentication
async def get_current_user(
    token: str = Depends(security)
) -> str:
    """Extract user ID from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

### CORS Configuration
```python
# CORS setup for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Database Management

### Alembic Migrations
```python
# Auto-generate migration
alembic revision --autogenerate -m "Add tasks table"

# Migration template
def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
```

### Database Connection
```python
# Production-ready connection
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    with Session(engine) as session:
        yield session
```

## MCP Tool Integration

### MCP Server Setup
```python
# MCP server for AI agent
class TodoMCPServer:
    def __init__(self):
        self.app = Server("todo-mcp-server")
        self.tools = {
            "add_task": self.add_task_tool,
            "list_tasks": self.list_tasks_tool,
            "complete_task": self.complete_task_tool
        }

    async def add_task_tool(self, arguments: dict):
        """Create task via MCP."""
        # Implementation
```

### Tool Schemas
```python
# MCP tool definition
ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Create a new task",
    "inputSchema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "maxLength": 200},
            "description": {"type": "string", "maxLength": 1000}
        },
        "required": ["title"]
    }
}
```

## Error Handling Patterns

### HTTP Exceptions
```python
# Standard error responses
class TaskNotFound(HTTPException):
    def __init__(self, task_id: int):
        super().__init__(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

class ValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=422,
            detail=f"Validation error: {message}"
        )
```

### Global Exception Handler
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
```

## Performance Optimization

### Database Query Optimization
```python
# Efficient queries with selects
def get_user_tasks(
    session: Session,
    user_id: str,
    limit: int = 100,
    offset: int = 0
) -> List[Task]:
    """Get user's tasks with pagination."""
    statement = select(Task).where(
        Task.user_id == user_id
    ).offset(offset).limit(limit)
    return session.exec(statement).all()
```

### Async Operations
```python
# Async database operations
async def create_task_async(
    session: AsyncSession,
    task_data: TaskCreate
) -> Task:
    """Asynchronous task creation."""
    task = Task(**task_data.dict())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

## Testing Strategy

### Pytest Setup
```python
# Test configuration
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_session] = lambda: test_db
    with TestClient(app) as c:
        yield c
```

### Endpoint Tests
```python
def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks",
        json={"title": "Test task"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test task"
```

## Security Implementation

### Input Validation
```python
# Pydantic models for validation
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=1000)

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

### SQL Injection Prevention
```python
# Safe queries with SQLModel
# Never use raw SQL with f-strings
tasks = session.exec(
    select(Task).where(
        Task.user_id == user_id,
        Task.title.like(f"%{search}%")
    )
).all()
```

## API Documentation

### OpenAPI Customization
```python
# Custom OpenAPI documentation
app = FastAPI(
    title="Todo API",
    description="RESTful API for task management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@router.get(
    "/tasks",
    response_model=List[TaskRead],
    summary="List all tasks",
    description="Retrieve all tasks for the authenticated user",
    responses={
        200: {"model": List[TaskRead], "description": "Task list"}
    }
)
```

## Deployment Configuration

### Environment Variables
```python
# Settings management
class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    cors_origins: List[str] = []

    class Config:
        env_file = ".env"

settings = Settings()
```

### Docker Support
```dockerfile
# Dockerfile for backend
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Integration Points

### With Frontend
- Type synchronization via Pydantic models
- API client generation from OpenAPI spec
- Shared type definitions

### With AI Systems
- MCP tool implementations
- State management for conversations
- Real-time chat endpoint

### With Database
- Connection pooling
- Migration management
- Query optimization

## Best Practices

### Code Organization
1. **Separate Concerns** - Models, routes, services, schemas
2. **Use Dependencies** - Database sessions, auth
3. **Type Hints** - Everywhere for clarity
4. **Error Boundaries** - Handle exceptions gracefully

### Database Design
1. **Foreign Keys** - Ensure data integrity
2. **Indexes** - Optimize query performance
3. **Constraints** - Validate at database level
4. **Migrations** - Version control schema changes

### API Design
1. **RESTful** - Follow HTTP semantics
2. **Consistent** - Standard response formats
3. **Versioning** - Support API evolution
4. **Documentation** - Keep OpenAPI updated