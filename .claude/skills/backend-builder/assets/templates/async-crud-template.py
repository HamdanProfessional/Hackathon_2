"""
Async CRUD Template for Evolution of TODO Project

This template provides the standard patterns for creating CRUD operations
with async/await, SQLModel, and FastAPI.

Copy this template and replace:
- MODEL_NAME: Your model name (e.g., Task, User, Comment)
- TABLE_NAME: Your database table name
- FIELD_DEFINITIONS: Your model fields
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, asc, desc
from sqlalchemy.orm import selectinload
from sqlmodel import Field, SQLModel

# =============================================================================
# MODEL TEMPLATE (app/models/MODEL_NAME.py)
# =============================================================================

class MODEL_NAME(SQLModel, table=True):
    """MODEL_NAME model."""
    __tablename__ = "TABLE_NAME"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    # Add your fields here
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default="")
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# CRUD TEMPLATE (app/crud/MODEL_NAME.py)
# =============================================================================

async def create_MODEL_NAME(db: AsyncSession, obj_data: MODEL_NAMECreate, user_id: str) -> MODEL_NAME:
    """Create a new MODEL_NAME."""
    db_obj = MODEL_NAME(
        user_id=user_id,
        **obj_data.dict()
    )

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)

    return db_obj


async def get_MODEL_NAMES_by_user(
    db: AsyncSession,
    user_id: str,
    search: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = 20,
    offset: Optional[int] = 0
) -> List[MODEL_NAME]:
    """Get MODEL_NAMES for user with filtering."""
    query = select(MODEL_NAME).where(MODEL_NAME.user_id == user_id)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                MODEL_NAME.title.ilike(search_term),
                MODEL_NAME.description.ilike(search_term)
            )
        )

    # Apply status filter
    if status == "completed":
        query = query.where(MODEL_NAME.completed == True)
    elif status == "pending":
        query = query.where(MODEL_NAME.completed == False)

    # Apply pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


async def get_MODEL_NAME_by_id(db: AsyncSession, obj_id: int, user_id: str) -> Optional[MODEL_NAME]:
    """Get MODEL_NAME by ID with ownership verification."""
    result = await db.execute(
        select(MODEL_NAME).where(
            MODEL_NAME.id == obj_id,
            MODEL_NAME.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def update_MODEL_NAME(
    db: AsyncSession,
    obj: MODEL_NAME,
    obj_data: MODEL_NAMEUpdate
) -> MODEL_NAME:
    """Update MODEL_NAME with partial field support."""
    # Update only provided fields
    field_data = obj_data.dict(exclude_unset=True)

    for field, value in field_data.items():
        setattr(obj, field, value)

    await db.commit()
    await db.refresh(obj)

    return obj


async def delete_MODEL_NAME(db: AsyncSession, obj: MODEL_NAME) -> None:
    """Delete a MODEL_NAME."""
    await db.delete(obj)
    await db.commit()


# =============================================================================
# ROUTER TEMPLATE (app/api/MODEL_NAME.py)
# =============================================================================

from fastapi import APIRouter, Depends, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.MODEL_NAME import MODEL_NAMECreate, MODEL_NAMEUpdate, MODEL_NAMEResponse
from app.crud import MODEL_NAME as MODEL_NAME_crud
from app.api.deps import get_current_user
from app.utils.exceptions import NotFoundException


router = APIRouter()


@router.post(
    "",
    response_model=MODEL_NAMEResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new MODEL_NAME",
)
async def create_MODEL_NAME(
    obj_data: MODEL_NAMECreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new MODEL_NAME."""
    new_obj = await MODEL_NAME_crud.create_MODEL_NAME(db, obj_data, str(current_user.id))
    return new_obj


@router.get(
    "",
    response_model=list[MODEL_NAMEResponse],
    summary="Get all MODEL_NAMES for current user",
)
async def get_MODEL_NAMES(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: Optional[int] = Query(20, ge=1, le=100),
    offset: Optional[int] = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get MODEL_NAMES with filtering and pagination."""
    objs = await MODEL_NAME_crud.get_MODEL_NAMES_by_user(
        db=db,
        user_id=str(current_user.id),
        search=search,
        status=status,
        limit=limit,
        offset=offset
    )
    return objs


@router.get(
    "/{obj_id}",
    response_model=MODEL_NAMEResponse,
    summary="Get a specific MODEL_NAME",
)
async def get_MODEL_NAME(
    obj_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get MODEL_NAME by ID."""
    obj = await MODEL_NAME_crud.get_MODEL_NAME_by_id(db, obj_id, str(current_user.id))
    if not obj:
        raise NotFoundException(detail=f"MODEL_NAME {obj_id} not found")
    return obj


@router.put(
    "/{obj_id}",
    response_model=MODEL_NAMEResponse,
    summary="Update a MODEL_NAME",
)
async def update_MODEL_NAME(
    obj_id: int,
    obj_data: MODEL_NAMEUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update MODEL_NAME fields."""
    obj = await MODEL_NAME_crud.get_MODEL_NAME_by_id(db, obj_id, str(current_user.id))
    if not obj:
        raise NotFoundException(detail=f"MODEL_NAME {obj_id} not found")

    updated_obj = await MODEL_NAME_crud.update_MODEL_NAME(db, obj, obj_data)
    return updated_obj


@router.delete(
    "/{obj_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a MODEL_NAME",
)
async def delete_MODEL_NAME(
    obj_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a MODEL_NAME permanently."""
    obj = await MODEL_NAME_crud.get_MODEL_NAME_by_id(db, obj_id, str(current_user.id))
    if not obj:
        raise NotFoundException(detail=f"MODEL_NAME {obj_id} not found")

    await MODEL_NAME_crud.delete_MODEL_NAME(db, obj)


# =============================================================================
# DEPENDENCY TEMPLATE (app/api/deps.py)
# =============================================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.config import settings
from app.database import get_db
from app.models.user import User


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Query user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


# =============================================================================
# CUSTOM EXCEPTIONS (app/utils/exceptions.py)
# =============================================================================

from fastapi import HTTPException


class NotFoundException(HTTPException):
    """Exception for resource not found (404)."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class ForbiddenException(HTTPException):
    """Exception for access denied (403)."""
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=403, detail=detail)


class ValidationException(HTTPException):
    """Exception for validation errors (400)."""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=400, detail=detail)
