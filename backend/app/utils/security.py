"""Security utilities for password hashing and JWT token management."""
import bcrypt
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.config import settings


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    # bcrypt has a 72 byte limit, truncate if necessary
    if len(password.encode('utf-8')) > 72:
        password = password[:72]

    # Hash using bcrypt directly
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    # bcrypt has a 72 byte limit, truncate if necessary
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]

    # Verify using bcrypt directly
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (typically {"sub": user_id, "email": user_email})
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    print(f"DEBUG: Creating token with data: {to_encode}")
    print(f"DEBUG: Using JWT_SECRET: {settings.JWT_SECRET_KEY[:5]}...")

    # Encode JWT token
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    print(f"DEBUG: Created token: {encoded_jwt[:20]}...")

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.

    This function performs critical security validation:
    - Verifies token signature using secret key
    - Checks expiration claim automatically
    - Validates token structure and format

    Args:
        token: JWT token string from Authorization header

    Returns:
        Decoded token payload if valid, None otherwise
        Returns None for ANY validation error (expired, invalid signature, malformed)
    """
    try:
        print(f"DEBUG: Decoding token: {token[:20]}...")
        print(f"DEBUG: Using JWT_SECRET for decode: {settings.JWT_SECRET_KEY[:5]}...")
        print(f"DEBUG: Using algorithm: {settings.JWT_ALGORITHM}")

        # jwt.decode() automatically validates:
        # 1. Signature matching
        # 2. Expiration (exp claim)
        # 3. Not before (nbf claim) if present
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        print(f"DEBUG: Successfully decoded token payload: {payload}")
        return payload
    except JWTError as e:
        # Catch any JWT validation error:
        # - ExpiredSignatureError
        # - InvalidTokenError
        # - DecodeError
        # All should be treated the same: reject the token
        print(f"DEBUG: JWT decode error: {type(e).__name__}: {str(e)}")
        return None
