"""API dependencies for database session and authentication."""
from typing import AsyncGenerator, Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.crud.user import get_user_by_id
from app.utils.security import decode_token
from app.utils.exceptions import UnauthorizedException


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        authorization: Authorization header with Bearer token
        db: Database session

    Returns:
        Current user instance

    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    if not authorization:
        raise UnauthorizedException(detail="Authorization header missing")

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(detail="Invalid authorization header format")

    token = parts[1]

    # Decode and validate token
    payload = decode_token(token)
    if payload is None:
        raise UnauthorizedException(detail="Invalid or expired token")

    # Get user ID from token payload
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(detail="Invalid token payload")

    # Fetch user from database
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise UnauthorizedException(detail="User not found")

    return user
