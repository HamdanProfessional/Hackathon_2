"""Authentication API endpoints.

Enhanced for Better Auth integration with JWT tokens.
Updated /me endpoint with database lookup.
"""
from fastapi import APIRouter, Depends, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import create_user, get_user_by_email, get_user_by_id
from app.utils.security import verify_password, create_access_token, decode_token
from app.utils.exceptions import ConflictException, UnauthorizedException
from app.utils.rate_limit import conditional_rate_limit

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def user_to_dict(user) -> dict:
    """Convert User model to dict for Better Auth compatibility."""
    return {
        "id": str(user.id),  # Better Auth expects string IDs
        "email": user.email,
        "name": getattr(user, 'name', None) or user.email.split("@")[0],  # Use name field or email prefix
        "createdAt": user.created_at.isoformat() if user.created_at else None,
        "updatedAt": user.created_at.isoformat() if user.created_at else None,  # Use created_at as fallback
    }


@router.get(
    "/me",
    summary="Get current user",
    description="Get the currently authenticated user from JWT token",
)
async def get_current_user_endpoint(
    authorization: str = Header(..., description="JWT bearer token"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user from JWT token.

    This endpoint is used by Better Auth to verify sessions.
    The token should be passed as: Authorization: Bearer <token>
    """
    # Extract token from "Bearer <token>" format
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    # Decode and verify token
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException(detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(detail="Invalid token: missing subject")

    # Get user from database using the injected session
    user = await get_user_by_id(db, user_id)
    if not user:
        raise UnauthorizedException(detail="User not found")

    return user_to_dict(user)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return an access token with user info (Better Auth compatible)",
)
@conditional_rate_limit(limiter, "5/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Password (minimum 8 characters)

    Returns JWT access token and user information for Better Auth integration.
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise ConflictException(detail="Email already registered")

    # Create new user
    new_user = await create_user(db, user_data)

    # Generate access token (sub must be string per JWT spec)
    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})

    # Return token with user info for Better Auth
    return TokenResponse(
        access_token=access_token,
        user=user_to_dict(new_user)
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user and return an access token with user info (Better Auth compatible)",
)
@conditional_rate_limit(limiter, "5/minute")
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user with email and password.

    - **email**: User email address
    - **password**: User password

    Returns JWT access token and user information for Better Auth integration.
    """
    # Get user by email
    user = await get_user_by_email(db, credentials.email)
    if not user:
        raise UnauthorizedException(detail="Invalid email or password")

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedException(detail="Invalid email or password")

    # Generate access token (sub must be string per JWT spec)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    # Return token with user info for Better Auth
    return TokenResponse(
        access_token=access_token,
        user=user_to_dict(user)
    )
