"""
CRUD Router Template
Generate fast CRUD endpoints with this template.
"""
from typing import List, Optional, Type
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session

def create_crud_router(
    model: Type,
    prefix: str,
    tags: List[str],
    create_schema: Type,
    update_schema: Type,
    read_schema: Type
) -> APIRouter:
    """Generate CRUD router for any SQLModel."""

    router = APIRouter(prefix=prefix, tags=tags)

    @router.post("/", response_model=read_schema)
    async def create(
        item: create_schema,
        session: Session = Depends(get_session)
    ):
        db_item = model.from_orm(item)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

    @router.get("/", response_model=List[read_schema])
    async def list_items(
        offset: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
    ):
        items = session.exec(select(model).offset(offset).limit(limit)).all()
        return items

    @router.get("/{item_id}", response_model=read_schema)
    async def get_item(
        item_id: int,
        session: Session = Depends(get_session)
    ):
        item = session.get(model, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Not found")
        return item

    @router.patch("/{item_id}", response_model=read_schema)
    async def update_item(
        item_id: int,
        item: update_schema,
        session: Session = Depends(get_session)
    ):
        db_item = session.get(model, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Not found")
        item_data = item.dict(exclude_unset=True)
        for key, value in item_data.items():
            setattr(db_item, key, value)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

    @router.delete("/{item_id}")
    async def delete_item(
        item_id: int,
        session: Session = Depends(get_session)
    ):
        item = session.get(model, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Not found")
        session.delete(item)
        session.commit()
        return {"ok": True}

    return router
