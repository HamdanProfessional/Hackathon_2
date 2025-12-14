"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import create_user, get_user_by_email
from app.utils.security import verify_password, create_access_token
from app.utils.exceptions import ConflictException, UnauthorizedException

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return an access token",
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Password (minimum 6 characters)

    Returns JWT access token for immediate authentication.
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise ConflictException(detail="Email already registered")

    # Create new user
    new_user = await create_user(db, user_data)

    # Generate access token
    access_token = create_access_token(data={"sub": new_user.id})

    return TokenResponse(access_token=access_token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user and return an access token",
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user with email and password.

    - **email**: User email address
    - **password**: User password

    Returns JWT access token for authenticated requests.
    """
    # Get user by email
    user = await get_user_by_email(db, credentials.email)
    if not user:
        raise UnauthorizedException(detail="Invalid email or password")

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedException(detail="Invalid email or password")

    # Generate access token
    access_token = create_access_token(data={"sub": user.id})

    return TokenResponse(access_token=access_token)
