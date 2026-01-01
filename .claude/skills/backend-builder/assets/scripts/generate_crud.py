#!/usr/bin/env python3
"""
FastAPI Backend CRUD Generator
Generates complete CRUD endpoints for SQLModel models.
"""
import os
from pathlib import Path

def generate_crud_code(model_name: str, fields: list) -> str:
    """Generate CRUD router code."""
    field_defs = "\n    ".join([f"{f['name']}: {f['type']}" for f in fields])

    return f'''from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, Field
from app.database import get_session
from app.models.{model_name.lower()} import {model_name}, {model_name}Create, {model_name}Update, {model_name}Read

router = APIRouter(prefix="/api/{model_name.lower()}s", tags=["{model_name.lower()}s"])

@router.post("/", response_model={model_name}Read)
async def create_{model_name.lower()}(
    item: {model_name}Create,
    session: Session = Depends(get_session)
):
    """Create a new {model_name}.**)
    db_item = {model_name}.from_orm(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/", response_model=List[{model_name}Read])
async def list_{model_name.lower()}s(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """List all {model_name}s with pagination."""
    items = session.exec(select({model_name}).offset(offset).limit(limit)).all()
    return items

@router.get("/{{item_id}}", response_model={model_name}Read)
async def get_{model_name.lower()}(
    item_id: int,
    session: Session = Depends(get_session)
):
    """Get a {model_name} by ID."""
    item = session.get({model_name}, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return item

@router.patch("/{{item_id}}", response_model={model_name}Read)
async def update_{model_name.lower()}(
    item_id: int,
    item: {model_name}Update,
    session: Session = Depends(get_session)
):
    """Update a {model_name}.**)
    db_item = session.get({model_name}, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    item_data = item.dict(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/{{item_id}}")
async def delete_{model_name.lower()}(
    item_id: int,
    session: Session = Depends(get_session)
):
    """Delete a {model_name}.**)
    item = session.get({model_name}, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    session.delete(item)
    session.commit()
    return {{"ok": True}}
'''

if __name__ == "__main__":
    # Example usage
    model = "Task"
    fields = [
        {"name": "title", "type": "str"},
        {"name": "description", "type": "Optional[str]"},
        {"name": "completed", "type": "bool"},
    ]
    print(generate_crud_code(model, fields))
