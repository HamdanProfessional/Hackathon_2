---
name: backend-builder
description: Complete FastAPI backend scaffolding including vertical slices (Model, Schema, Router), CRUD generation, endpoint creation, SQLModel models, JWT authentication, and pytest tests. Ideal for Phase II backend implementations.
version: 1.0.0
category: backend
tags: [fastapi, backend, crud, sqlmodel, scaffolding, python, jwt, authentication]
dependencies: [fastapi, sqlmodel, uvicorn, pytest, pydantic]
---

# Backend Builder Skill

Comprehensive FastAPI backend development and scaffolding.

## When to Use This Skill

Use this skill when:
- Scaffolding complete backend features (Model, Schema, Router)
- Creating CRUD endpoints with SQLModel
- Generating custom FastAPI endpoints
- Implementing JWT authentication
- Adding database models and migrations
- Writing pytest tests for backend

---

## Scaffolding Workflow

1. Read Spec: Read `@specs/features/[feature-name].md` for data model and API contract
2. Model Generation: Create SQLModel class in `backend/app/models/[feature].py`
3. Schema Generation: Create Pydantic DTOs in `backend/app/schemas/[feature].py`
4. Router Creation: Create FastAPI router in `backend/app/routers/[feature].py`
5. Security Integration: Inject `Depends(get_current_user)` on ALL endpoints
6. Multi-User Isolation: Filter queries by `user_id` from JWT
7. Test Generation: Create pytest tests in `backend/tests/test_[feature].py`
8. Registration: Update `backend/app/main.py` to include router

---

## Model Template

```python
"""
[Feature] SQLModel for TODO application.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel, Index


class [FeatureName](SQLModel, table=True):
    """
    [Feature] model for multi-user TODO application.
    """
    __tablename__ = "[table_name]"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key to users table
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="User who owns this resource"
    )

    # Feature-specific fields
    [field_name]: [type] = Field(
        [constraints],
        description="[description]"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Schema Template

```python
"""
[Feature] Pydantic schemas for API validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional


class [Feature]Base(BaseModel):
    """Base schema with common fields."""
    [field]: [type] = Field(..., description="[description]")


class [Feature]Create([Feature]Base):
    """Schema for creating a new resource."""
    @validator('[field]')
    def validate_[field](cls, v):
        if [condition]:
            raise ValueError('[error message]')
        return v


class [Feature]Update(BaseModel):
    """Schema for updating (all fields optional)."""
    [field]: Optional[type] = Field(None)


class [Feature]Read([Feature]Base):
    """Schema for responses (includes auto-generated fields)."""
    id: int
    user_id: str  # UUID as string
    created_at: datetime
    updated_at: datetime
```

---

## Router Template (CRUD)

```python
"""
[Feature] API routes with CRUD operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from uuid import UUID

from app.database import get_session
from app.models.[feature] import [Feature]
from app.schemas.[feature] import [Feature]Read, [Feature]Create, [Feature]Update
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api", tags=["[Features]"])


@router.get("/{user_id}/[features]", response_model=list[[Feature]Read])
async def get_[features](
    user_id: UUID,
    current_user: UUID = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all resources for a user."""
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    statement = select([Feature]).where([Feature].user_id == user_id)
    [features] = session.exec(statement).all()
    return [features]


@router.post("/{user_id}/[features]", response_model=[Feature]Read, status_code=201)
async def create_[feature](
    user_id: UUID,
    data: [Feature]Create,
    current_user: UUID = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new resource."""
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    new_[feature] = [Feature](user_id=current_user, **data.dict())
    session.add(new_[feature])
    session.commit()
    session.refresh(new_[feature])
    return new_[feature]


@router.put("/{user_id}/[features]/{[feature]_id}", response_model=[Feature]Read)
async def update_[feature](
    user_id: UUID,
    [feature]_id: int,
    data: [Feature]Update,
    current_user: UUID = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update an existing resource."""
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    statement = select([Feature]).where(
        [Feature].id == [feature]_id,
        [Feature].user_id == user_id
    )
    [feature] = session.exec(statement).first()

    if not [feature]:
        raise HTTPException(status_code=404, detail="Not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr([feature], field, value)

    session.add([feature])
    session.commit()
    session.refresh([feature])
    return [feature]


@router.delete("/{user_id}/[features]/{[feature]_id}")
async def delete_[feature](
    user_id: UUID,
    [feature]_id: int,
    current_user: UUID = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a resource."""
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Access forbidden")

    statement = select([Feature]).where(
        [Feature].id == [feature]_id,
        [Feature].user_id == user_id
    )
    [feature] = session.exec(statement).first()

    if not [feature]:
        raise HTTPException(status_code=404, detail="Not found")

    session.delete([feature])
    session.commit()
    return {"detail": "Deleted"}
```

---

## Custom Endpoints

### Statistics Endpoint

```python
@router.get("/stats", response_model=TaskStatsResponse)
async def get_task_statistics(
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get task statistics for the current user."""
    from sqlmodel import func

    total = session.exec(
        select(func.count(Task.id)).where(Task.user_id == user_id)
    ).one()

    completed = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.status == "completed"
        )
    ).one()

    completion_rate = (completed / total * 100) if total > 0 else 0.0

    return TaskStatsResponse(
        total=total,
        completed=completed,
        completion_rate=round(completion_rate, 2)
    )
```

### Batch Operations

```python
@router.post("/bulk-complete", response_model=TaskBulkCompleteResponse)
async def bulk_complete_tasks(
    request: TaskBulkCompleteRequest,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Mark multiple tasks as completed."""
    updated_count = 0
    failed_ids = []

    for task_id in request.task_ids:
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = session.exec(statement).first()

        if task:
            task.status = "completed"
            session.add(task)
            updated_count += 1
        else:
            failed_ids.append(task_id)

    session.commit()

    return TaskBulkCompleteResponse(
        updated_count=updated_count,
        failed_ids=failed_ids
    )
```

### Search Endpoint

```python
@router.get("/search", response_model=TaskListResponse)
async def search_tasks(
    query: str = Query(..., min_length=1),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Search tasks by title and description."""
    from sqlmodel import or_

    statement = select(Task).where(Task.user_id == user_id)

    search_filter = or_(
        Task.title.ilike(f"%{query}%"),
        Task.description.ilike(f"%{query}%")
    )
    statement = statement.where(search_filter)

    if status:
        statement = statement.where(Task.status == status)

    total = len(session.exec(statement).all())

    offset = (page - 1) * page_size
    tasks = session.exec(
        statement.offset(offset).limit(page_size)
    ).all()

    return TaskListResponse(items=tasks, total=total, page=page)
```

---

## Test Template

```python
"""
Tests for [Feature] API endpoints.
"""
import pytest
from httpx import AsyncClient


class Test[Feature]Operations:
    """Test CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_[feature](
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user
    ):
        """Test creating a new resource."""
        response = await client.post(
            f"/api/{test_user.id}/[features]",
            json={"[field]": "value"},
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["[field]"] == "value"

    @pytest.mark.asyncio
    async def test_list_[features](
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user
    ):
        """Test listing resources."""
        response = await client.get(
            f"/api/{test_user.id}/[features]",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test that unauthorized requests are rejected."""
        response = await client.get("/api/some-user-id/[features]")
        assert response.status_code == 401
```

---

## Post-Scaffolding Steps

1. Update main.py:
```python
from app.routers import [feature]
app.include_router([feature].router)
```

2. Restart backend:
```bash
cd backend
uvicorn app.main:app --reload
```

3. Run tests:
```bash
cd backend
pytest tests/test_[feature].py -v
```

4. Test with Swagger: http://localhost:8000/docs

---

## Quality Checklist

Before finalizing:
- [ ] All fields in model match the spec
- [ ] All endpoints have `Depends(get_current_user)`
- [ ] All queries filter by `user_id`
- [ ] Authorization check compares path `user_id` with JWT
- [ ] Timestamps (created_at, updated_at) included
- [ ] Response schemas convert UUID to string
- [ ] Error handling with appropriate HTTP codes
- [ ] Pytest tests cover main CRUD operations
- [ ] Router registered in main.py
- [ ] Swagger docs accessible at /docs
