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
    print(f"DEBUG: Authorization header: {authorization}")

    if not authorization:
        print("DEBUG: No authorization header found")
        raise UnauthorizedException(detail="Authorization header missing")

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        print(f"DEBUG: Invalid authorization format. Parts: {parts}")
        raise UnauthorizedException(detail="Invalid authorization header format")

    token = parts[1]
    print(f"DEBUG: Received Token: {token[:20]}...")

    # Decode and validate token
    payload = decode_token(token)
    if payload is None:
        print("DEBUG: Token decode returned None")
        raise UnauthorizedException(detail="Invalid or expired token")

    print(f"DEBUG: Decoded Payload: {payload}")

    # Get user ID from token payload (sub is string per JWT spec, convert to int)
    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        print("DEBUG: No user_id (sub) in token payload")
        raise UnauthorizedException(detail="Invalid token payload")

    # user_id is already a UUID string, no need to convert to int
    print(f"DEBUG: Looking for user_id: {user_id_str}")

    # Fetch user from database
    user = await get_user_by_id(db, user_id_str)
    if user is None:
        print(f"DEBUG: User not found for ID: {user_id}")
        raise UnauthorizedException(detail="User not found")

    print(f"DEBUG: Successfully authenticated user: {user.email}")

    return user
