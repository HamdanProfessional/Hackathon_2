---
name: backend-scaffolder
description: Scaffolds complete FastAPI backends with SQLModel models, Pydantic schemas, and CRUD endpoints. Generates type-safe database operations, request/response models, and API routes with validation. Use when building Phase II full-stack applications or any FastAPI project needing database integration.
---

# Backend Scaffolder

## Quick Start

```python
# Scaffold complete CRUD for a model
from backend_scaffolder import create_crud

create_crud(
    model_name="Task",
    fields=[
        ("title", "str", {"required": True, "max_length": 200}),
        ("description", "str", {"required": False, "max_length": 1000}),
        ("completed", "bool", {"default": False})
    ],
    user_field=True  # Add user_id for multi-tenant
)

# Output:
# - models/task.py (SQLModel)
# - schemas/task.py (Pydantic)
# - routes/tasks.py (FastAPI routes)
# - services/task_service.py (Business logic)
```

## Generated Structure

```
backend/app/
├── models/
│   ├── __init__.py
│   ├── base.py          # Base SQLModel class
│   ├── user.py          # User model
│   └── task.py          # Task model
├── schemas/
│   ├── __init__.py
│   ├── task.py          # Pydantic schemas
│   └── user.py          # User schemas
├── routes/
│   ├── __init__.py
│   ├── tasks.py         # Task endpoints
│   └── auth.py          # Auth endpoints
├── services/
│   ├── __init__.py
│   └── task_service.py  # Task business logic
├── database.py          # Database setup
└── main.py              # FastAPI app
```

## Model Generation

### SQLModel with Relationships
```python
# models/task.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class TaskBase(SQLModel):
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default="", max_length=1000)
    completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")

# Create/Update schemas
class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# Response schemas
class TaskRead(TaskBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
```

### User Model with Auth
```python
# models/user.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List

class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    name: Optional[str] = None

class User(UserBase, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")

class UserRead(UserBase):
    id: str
    created_at: datetime

class UserCreate(SQLModel):
    email: str
    password: str
    name: Optional[str] = None
```

## Route Generation

### Full CRUD Endpoints
```python
# routes/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Create a new task for the authenticated user."""
    db_task = Task.from_orm(task, update={"user_id": current_user})
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskRead])
async def list_tasks(
    status: str = Query("all", regex="^(all|pending|completed)$"),
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """List all tasks for the authenticated user with optional filtering."""
    query = select(Task).where(Task.user_id == current_user)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    tasks = session.exec(query).all()
    return tasks

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Get a specific task by ID."""
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Update a task."""
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update fields
    task_data = task_update.dict(exclude_unset=True)
    for field, value in task_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """Delete a task."""
    task = session.get(Task, task_id)
    if not task or task.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}
```

## Service Layer

### Business Logic Separation
```python
# services/task_service.py
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

class TaskService:
    def __init__(self, session: Session):
        self.session = session

    def create_task(self, user_id: str, task_data: TaskCreate) -> Task:
        """Create a new task with business logic validation."""
        # Business rules
        if len(task_data.title) < 3:
            raise ValueError("Task title must be at least 3 characters")

        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description or "",
            completed=task_data.completed
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_user_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """Get tasks with filtering and pagination."""
        query = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)

        query = query.offset(offset).limit(limit)
        return self.session.exec(query).all()

    def get_task_stats(self, user_id: str) -> dict:
        """Get task statistics for dashboard."""
        total = len(self.session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all())

        completed = len(self.session.exec(
            select(Task).where(
                Task.user_id == user_id,
                Task.completed == True
            )
        ).all())

        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "completion_rate": completed / total if total > 0 else 0
        }
```

## Database Setup

### Engine and Session Management
```python
# database.py
from sqlmodel import create_engine, Session
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session

def init_db():
    """Create database tables."""
    from models import Task, User  # Import all models
    SQLModel.metadata.create_all(engine)
```

## Authentication Integration

### JWT Dependencies
```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

async def get_current_user(
    token: str = Depends(security)
) -> str:
    """Extract user ID from JWT token."""
    try:
        payload = jwt.decode(
            token.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

## Testing Setup

### Test Fixtures
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from database import get_session
from main import app

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_session] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### CRUD Tests
```python
# tests/test_tasks.py
def test_create_task(client):
    """Test creating a new task."""
    response = client.post(
        "/api/tasks",
        json={
            "title": "Test task",
            "description": "Test description"
        },
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert "id" in data

def test_list_tasks(client):
    """Test listing tasks."""
    # Create a task first
    client.post(
        "/api/tasks",
        json={"title": "Test task"},
        headers={"Authorization": "Bearer valid_token"}
    )

    response = client.get(
        "/api/tasks",
        headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test task"
```

## Customization Options

### Model Customization
```python
# Add custom fields and relationships
create_crud(
    model_name="Task",
    fields=[
        ("title", "str", {"required": True, "max_length": 200}),
        ("description", "str", {"required": False}),
        ("priority", "str", {"default": "medium", "choices": ["low", "medium", "high"]}),
        ("due_date", "datetime", {"required": False})
    ],
    user_field=True,
    soft_delete=True,  # Add deleted_at field
    timestamps=True    # Add created_at, updated_at
)
```

### Route Customization
```python
# Custom endpoints
create_crud(
    model_name="Task",
    custom_routes=[
        ("PATCH", "/{id}/complete", "toggle_complete"),
        ("GET", "/stats", "get_stats"),
        ("POST", "/bulk", "bulk_create")
    ]
)
```

## Best Practices

1. **Always use transactions** for multi-table operations
2. **Validate input** at both schema and service layer
3. **Use select()** for queries to be explicit
4. **Handle relationships** properly in schemas
5. **Add indexes** for query performance
6. **Use environment variables** for sensitive data
7. **Implement proper error handling** with HTTP status codes
8. **Write tests** for all CRUD operations

## Migration Path

### For Phase III (AI Chatbot)
1. Keep same Task model structure
2. Add conversation relationships
3. Extend service layer with AI-specific methods
4. Convert endpoints to MCP tools