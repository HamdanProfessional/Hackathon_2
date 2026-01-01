#!/usr/bin/env python3
"""Generate CRUD operations for a SQLModel resource."""
import argparse
from pathlib import Path
from typing import List

MODEL_TEMPLATE = '''# backend/app/models/{resource_lower}.py
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Index

class {Resource}(SQLModel, table=True):
    """{Resource} model."""
    __tablename__ = "{resource_lower}s"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
{fields}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("ix_{resource_lower}s_user_id", "user_id"),
    )
'''

SCHEMA_TEMPLATE = '''# backend/app/schemas/{resource_lower}.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class {Resource}Create(BaseModel):
    """Schema for creating a {resource}."""
{create_fields}

class {Resource}Update(BaseModel):
    """Schema for updating a {resource}."""
{update_fields}

class {Resource}Response(BaseModel):
    """Schema for {resource} response."""
{response_fields}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
'''

ROUTER_TEMPLATE = '''# backend/app/routers/{resource_lower}.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from uuid import UUID

from app.database import get_session
from app.models.{resource_lower} import {Resource}
from app.schemas.{resource_lower} import {Resource}Create, {Resource}Update, {Resource}Response
from app.auth import get_current_user_id

router = APIRouter(prefix="/{resource_lower}s", tags=["{Resource}s"])

@router.post("/", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource_lower}(
    data: {Resource}Create,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a new {resource}."""
    {resource} = {Resource}(user_id=user_id, **data.model_dump())
    session.add({resource})
    session.commit()
    session.refresh({resource})
    return {resource}

@router.get("/", response_model=list[{Resource}Response])
async def list_{resource_lower}s(
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """List all {resource_lower}s for current user."""
    {resource_lower}s = session.exec(
        select({Resource}).where({Resource}.user_id == user_id)
    ).all()
    return {resource_lower}s

@router.get("/{{{resource_lower}_id}}", response_model={Resource}Response)
async def get_{resource_lower}(
    {resource_lower}_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get a specific {resource} by ID."""
    {resource} = session.get({Resource}, {resource_lower}_id)
    if not {resource} or {resource}.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{Resource} not found")
    return {resource}

@router.patch("/{{{resource_lower}_id}}", response_model={Resource}Response)
async def update_{resource_lower}(
    {resource_lower}_id: int,
    data: {Resource}Update,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Update a {resource}."""
    {resource} = session.get({Resource}, {resource_lower}_id)
    if not {resource} or {resource}.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{Resource} not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr({resource}, key, value)

    {resource}.updated_at = datetime.utcnow()
    session.add({resource})
    session.commit()
    session.refresh({resource})
    return {resource}

@router.delete("/{{{resource_lower}_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{resource_lower}(
    {resource_lower}_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Delete a {resource}."""
    {resource} = session.get({Resource}, {resource_lower}_id)
    if not {resource} or {resource}.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{Resource} not found")

    session.delete({resource})
    session.commit()
'''

TEST_TEMPLATE = '''# tests/test_{resource_lower}.py
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.models.{resource_lower} import {Resource}

client = TestClient(app)

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(test_user.id)
    return {{"Authorization": f"Bearer {{token}}"}}

def test_create_{resource_lower}(auth_headers):
    response = client.post(
        "/{resource_lower}s/",
        json={{"name": "Test {Resource}"}},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test {Resource}"

def test_list_{resource_lower}s(auth_headers):
    response = client.get("/{resource_lower}s/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_{resource_lower}_user_isolation(auth_headers, db_session):
    # Create for different user
    other_user_id = uuid4()
    {resource_lower} = {Resource}(user_id=other_user_id, name="Other")
    db_session.add({resource_lower})
    db_session.commit()

    # Try to access
    response = client.get(f"/{{{resource_lower}s/{{resource_lower}.id}}", headers=auth_headers)
    assert response.status_code == 404
'''


def generate_crud(resource_name: str, fields: List[str], output_dir: Path):
    """Generate CRUD files for a resource."""
    resource = resource_name.capitalize()
    resource_lower = resource_name.lower()

    # Parse fields
    field_lines = []
    create_fields = []
    update_fields = []
    response_fields = []

    for field in fields:
        name, type_ = field.split(":", 1)
        optional = type_.startswith("Optional[")

        field_lines.append(f'    {name}: {type_} = Field(default=None{"" if optional else ", nullable=False"})')

        if not optional and name != "user_id":
            create_fields.append(f'    {name}: {type_}')

        update_fields.append(f'    {name}: Optional[{type_.replace("Optional[", "").rstrip("]")}] = None')
        response_fields.append(f'    {name}: {type_.replace("Optional[", "").rstrip("]")}')

    # Create files
    models_dir = output_dir / "backend" / "app" / "models"
    schemas_dir = output_dir / "backend" / "app" / "schemas"
    routers_dir = output_dir / "backend" / "app" / "routers"
    tests_dir = output_dir / "backend" / "tests"

    for dir_path in [models_dir, schemas_dir, routers_dir, tests_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Write files
    (models_dir / f"{resource_lower}.py").write_text(
        MODEL_TEMPLATE.format(
            Resource=resource,
            resource_lower=resource_lower,
            fields="\n".join(field_lines)
        )
    )

    (schemas_dir / f"{resource_lower}.py").write_text(
        SCHEMA_TEMPLATE.format(
            Resource=resource,
            resource_lower=resource_lower,
            create_fields="\n".join(create_fields) if create_fields else "    pass",
            update_fields="\n".join(update_fields) if update_fields else "    pass",
            response_fields="\n".join(response_fields) if response_fields else "    pass"
        )
    )

    (routers_dir / f"{resource_lower}.py").write_text(
        ROUTER_TEMPLATE.format(Resource=resource, resource_lower=resource_lower)
    )

    (tests_dir / f"test_{resource_lower}.py").write_text(
        TEST_TEMPLATE.format(Resource=resource, resource_lower=resource_lower)
    )

    print(f"Generated CRUD for {resource_name}")
    print(f"  Model:     {models_dir / resource_lower}.py")
    print(f"  Schema:    {schemas_dir / resource_lower}.py")
    print(f"  Router:    {routers_dir / resource_lower}.py")
    print(f"  Tests:     {tests_dir / f'test_{resource_lower}.py'}")
    print(f"\nNext steps:")
    print(f"  1. Review generated files")
    print(f"  2. Run: alembic revision --autogenerate -m 'Add {resource}'")
    print(f"  3. Run: alembic upgrade head")
    print(f"  4. Add router to app/main.py: app.include_router({resource_lower}_router)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CRUD for SQLModel resource")
    parser.add_argument("resource", help="Resource name (e.g., task, project)")
    parser.add_argument("--fields", nargs="+", default=["title:str", "description:Optional[str]"],
                       help="Fields as name:type pairs")
    parser.add_argument("--output", default=".", help="Output directory")

    args = parser.parse_args()
    generate_crud(args.resource, args.fields, Path(args.output))
