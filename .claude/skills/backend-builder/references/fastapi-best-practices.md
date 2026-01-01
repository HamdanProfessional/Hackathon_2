# FastAPI Best Practices - Evolution of TODO Edition

This guide documents the actual patterns used in the Evolution of TODO project.

## Async Database Operations

### Always Use AsyncSession
```python
from sqlalchemy.ext.asyncio import AsyncSession

async def get_items(db: AsyncSession, user_id: str):
    result = await db.execute(select(Item).where(Item.user_id == user_id))
    return result.scalars().all()
```

### Eager Loading to Prevent N+1 Queries
```python
from sqlalchemy.orm import selectinload

# Load relationships eagerly
stmt = select(Task).options(selectinload(Task.priority_obj))
result = await db.execute(stmt)
```

### Commit and Refresh Pattern
```python
db.add(db_obj)
await db.commit()
await db.refresh(db_obj)

# Re-fetch with eager loading to prevent DetachedInstanceError
stmt = select(Model).where(Model.id == db_obj.id).options(selectinload(Model.relationship))
result = await db.execute(stmt)
return result.scalar_one()
```

## API Router Patterns

### Route Organization
```python
from fastapi import APIRouter, Depends, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task."""
    # Implementation
```

### Background Tasks for Non-Blocking Operations
```python
@router.post("")
async def create_task(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_task = await create_task(db, task_data, str(current_user.id))

    # Fire and forget - don't block response
    background_tasks.add_task(send_email, user_email, task_data)

    return new_task
```

### Proper Status Codes
- `200 OK` - Successful GET, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation errors
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Pydantic validation error
- `500 Internal Server Error` - Unexpected errors

## JWT Authentication

### Token Creation
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
```

### Dependency Injection
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Verify JWT and return current user."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

## Custom Exceptions

```python
# app/utils/exceptions.py
from fastapi import HTTPException

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=403, detail=detail)

class ValidationException(HTTPException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=400, detail=detail)

# Usage
@router.get("/{task_id}")
async def get_task(task_id: int):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise NotFoundException(detail=f"Task {task_id} not found")
    return task
```

## Dapr Event Publishing

### Fire-and-Forget Pattern
```python
from app.services.event_publisher import dapr_event_publisher

async def create_task(db: AsyncSession, task_data: TaskCreate, user_id: str):
    db_task = Task(**task_data.dict(), user_id=user_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    # Publish event (fire and forget - don't block response)
    try:
        event_data = {"task_id": db_task.id, "user_id": user_id}
        await dapr_event_publisher.publish_task_created(event_data)
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")

    return db_task
```

## Pydantic Schemas

### Request/Response Separation
```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    """Schema for creating a task."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)
    priority_id: int = Field(default=2)
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=10000)
    priority_id: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    """Schema for task response."""
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
```

## Configuration with Pydantic Settings

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # AI
    GROQ_API_KEY: str
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Email
    EMAIL_FROM_NAME: str = "Todo App"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Query Parameters with Validation

```python
@router.get("")
async def get_items(
    search: Optional[str] = Query(None, description="Search term"),
    status: Optional[str] = Query(None, regex="^(pending|completed|all)$"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|due_date|priority)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    limit: Optional[int] = Query(20, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get items with filtering and pagination."""
    # Implementation
```

## Health Check Endpoint

```python
@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {"status": "healthy", "service": "todo-backend"}
```

## Error Response Format

```python
{
    "detail": "Error message here"
}
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings/configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLModel models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routers
│   │   ├── deps.py          # Dependencies (get_current_user)
│   │   ├── tasks.py         # Task endpoints
│   │   └── ...
│   ├── crud/                # Database operations
│   ├── services/            # Business logic
│   └── utils/               # Utilities (email, exceptions)
├── alembic/                 # Database migrations
├── tests/                   # Tests
└── requirements.txt         # Dependencies
```
