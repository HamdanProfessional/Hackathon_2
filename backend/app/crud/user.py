"""User CRUD operations."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db: Database session
        user_data: User creation data

    Returns:
        Created user instance
    """
    hashed_password = hash_password(user_data.password)

    db_user = User(
        email=user_data.email,
        name=user_data.email.split("@")[0],  # Default name from email
        hashed_password=hashed_password,  # Use hashed_password consistently
        password_hash=hashed_password,    # Also set password_hash for compatibility
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get user by email address.

    Args:
        db: Database session
        email: User email

    Returns:
        User instance if found, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User ID (UUID string)

    Returns:
        User instance if found, None otherwise
    """
    # Import UUID for conversion
    import uuid

    try:
        # Convert string to UUID
        user_uuid = uuid.UUID(user_id)
        result = await db.execute(select(User).where(User.id == user_uuid))
        return result.scalar_one_or_none()
    except (ValueError, TypeError):
        # Invalid UUID format
        return None
