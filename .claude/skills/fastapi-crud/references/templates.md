# FastAPI CRUD - Reusable Templates

## Model Template

```python
# backend/app/models/{resource}.py
from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Index

class {Resource}(SQLModel, table=True):
    """{Resource} model."""
    __tablename__ = "{resource_lower}s"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = None
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("ix_{resource_lower}s_user_id", "user_id"),
        Index("ix_{resource_lower}s_user_status", "user_id", "status"),
    )
```

## Schema Template

```python
# backend/app/schemas/{resource}.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class {Resource}Create(BaseModel):
    """Schema for creating a {resource}."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="pending")

    @validator("status")
    def validate_status(cls, v):
        valid = ["pending", "in_progress", "completed"]
        if v not in valid:
            raise ValueError(f"Status must be one of: {valid}")
        return v

class {Resource}Update(BaseModel):
    """Schema for updating a {resource}."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None

class {Resource}Response(BaseModel):
    """Schema for {resource} response."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## Router Template

```python
# backend/app/routers/{resource}.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from uuid import UUID

from app.database import get_session
from app.models.{resource} import {Resource}
from app.schemas.{resource} import {Resource}Create, {Resource}Update, {Resource}Response
from app.auth import get_current_user_id

router = APIRouter(prefix="/{resource_lower}s", tags=["{Resource}s"])

@router.post("/", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource_lower}(
    data: {Resource}Create,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a new {resource}."""
    resource = {Resource}(user_id=user_id, **data.model_dump())
    session.add(resource)
    session.commit()
    session.refresh(resource)
    return resource

@router.get("/", response_model=list[{Resource}Response])
async def list_{resource_lower}s(
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """List all {resource_lower}s for current user."""
    resources = session.exec(
        select({Resource}).where({Resource}.user_id == user_id)
    ).all()
    return resources

@router.get("/{{{resource_lower}_id}}", response_model={Resource}Response)
async def get_{resource_lower}(
    {resource_lower}_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get a specific {resource} by ID."""
    resource = session.get({Resource}, {resource_lower}_id)
    if not resource or resource.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Resource} not found"
        )
    return resource

@router.patch("/{{{resource_lower}_id}}", response_model={Resource}Response)
async def update_{resource_lower}(
    {resource_lower}_id: int,
    data: {Resource}Update,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Update a {resource}."""
    resource = session.get({Resource}, {resource_lower}_id)
    if not resource or resource.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Resource} not found"
        )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(resource, key, value)

    resource.updated_at = datetime.utcnow()
    session.add(resource)
    session.commit()
    session.refresh(resource)
    return resource

@router.delete("/{{{resource_lower}_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{resource_lower}(
    {resource_lower}_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Delete a {resource}."""
    resource = session.get({Resource}, {resource_lower}_id)
    if not resource or resource.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{Resource} not found"
        )

    session.delete(resource)
    session.commit()
```

## Migration Template

```python
# alembic/versions/xxx_add_{resource}.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        '{resource_lower}s',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index('ix_{resource_lower}s_user_id', '{resource_lower}s', ['user_id'])
    op.create_index('ix_{resource_lower}s_user_status', '{resource_lower}s', ['user_id', 'status'])

def downgrade():
    op.drop_table('{resource_lower}s')
```

## Test Template

```python
# tests/test_{resource_lower}.py
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.models.{resource_lower} import {Resource}

client = TestClient(app)

@pytest.fixture
def auth_headers(test_user):
    from app.auth import create_access_token
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

def test_create_{resource_lower}(auth_headers, db_session):
    response = client.post(
        "/{resource_lower}s/",
        json={"title": "Test {Resource}"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test {Resource}"

def test_list_{resource_lower}s(auth_headers):
    response = client.get("/{resource_lower}s/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_{resource_lower}_user_isolation(auth_headers, db_session):
    # Create for different user
    other_user_id = uuid4()
    resource = {Resource}(user_id=other_user_id, title="Other {Resource}")
    db_session.add(resource)
    db_session.commit()

    # Try to access with different user
    response = client.get(f"/{{{resource_lower}s/{resource.id}}", headers=auth_headers)
    assert response.status_code == 404
```

## Registration Template

```python
# backend/app/main.py
from app.routers.{resource_lower} import router as {resource_lower}_router

app.include_router({resource_lower}_router)
```
