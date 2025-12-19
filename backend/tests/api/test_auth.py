"""Authentication API tests."""
import pytest
import asyncio
import jwt
from datetime import datetime, timedelta
from httpx import AsyncClient

from app.utils.security import create_access_token
from app.config import settings


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient):
    """
    Test T036: Registering a user with duplicate email returns 409 Conflict.

    This test validates that the system properly handles duplicate email registration attempts
    and returns an appropriate conflict status code with a descriptive error message.
    """
    test_user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
    }

    # First registration should succeed
    response = await client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Second registration with same email should fail
    response = await client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 409
    error_data = response.json()
    assert "detail" in error_data
    assert "already registered" in error_data["detail"].lower()


@pytest.mark.asyncio
async def test_login_invalid_credentials_returns_401(client: AsyncClient):
    """
    Test T037: Login with invalid credentials returns 401 Unauthorized.

    This test validates that the system properly rejects login attempts with:
    1. Non-existent email addresses
    2. Incorrect passwords for existing users
    Both scenarios should return 401 Unauthorized with appropriate error messages.
    """
    # Test login with non-existent email
    invalid_credentials = {
        "email": "nonexistent@example.com",
        "password": "anypassword",
    }
    response = await client.post("/api/auth/login", json=invalid_credentials)
    assert response.status_code == 401
    error_data = response.json()
    assert "detail" in error_data
    assert "invalid email or password" in error_data["detail"].lower()

    # Test login with wrong password for existing user
    test_user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
    }

    # First register a user
    await client.post("/api/auth/register", json=test_user_data)

    # Then try to login with wrong password
    wrong_password = {
        "email": test_user_data["email"],
        "password": "wrongpassword",
    }
    response = await client.post("/api/auth/login", json=wrong_password)
    assert response.status_code == 401
    error_data = response.json()
    assert "detail" in error_data
    assert "invalid email or password" in error_data["detail"].lower()


@pytest.mark.asyncio
async def test_login_with_valid_credentials_succeeds(client: AsyncClient):
    """
    Additional test: Login with valid credentials succeeds.

    This test ensures that the authentication flow works correctly when
    valid credentials are provided.
    """
    test_user_data = {
        "email": "validuser@example.com",
        "password": "validpassword123",
    }

    # Register user first
    await client.post("/api/auth/register", json=test_user_data)

    # Login with correct credentials
    response = await client.post("/api/auth/login", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_register_valid_user_succeeds(client: AsyncClient):
    """
    Additional test: Registering a valid user succeeds.

    This test validates the registration endpoint accepts valid user data
    and returns an access token for immediate authentication.
    """
    valid_user = {
        "email": "newuser@example.com",
        "password": "newpassword123",
    }

    response = await client.post("/api/auth/register", json=valid_user)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_register_invalid_email_fails(client: AsyncClient):
    """
    Additional test: Registering with invalid email fails.

    This test ensures the email validation properly rejects invalid formats.
    """
    invalid_user = {
        "email": "not-an-email",
        "password": "password123",
    }

    response = await client.post("/api/auth/register", json=invalid_user)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password_fails(client: AsyncClient):
    """
    Additional test: Registering with short password fails.

    This test ensures password validation enforces minimum length requirements.
    """
    short_password_user = {
        "email": "test@example.com",
        "password": "123",
    }

    response = await client.post("/api/auth/register", json=short_password_user)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_email_fails(client: AsyncClient):
    """
    Additional test: Login without email fails.

    This test validates that email is a required field for login.
    """
    response = await client.post("/api/auth/login", json={"password": "password123"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_password_fails(client: AsyncClient):
    """
    Additional test: Login without password fails.

    This test validates that password is a required field for login.
    """
    response = await client.post("/api/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_email_fails(client: AsyncClient):
    """
    Additional test: Register without email fails.

    This test validates that email is a required field for registration.
    """
    response = await client.post("/api/auth/register", json={"password": "password123"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_password_fails(client: AsyncClient):
    """
    Additional test: Register without password fails.

    This test validates that password is a required field for registration.
    """
    response = await client.post("/api/auth/register", json={"email": "test@example.com"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_token_with_invalid_signature_fails(client: AsyncClient):
    """
    Test T104: Using a token with invalid signature should be rejected.

    This test ensures that JWT tokens with invalid signatures are properly rejected
    by the authentication system.
    """
    # Create a valid user
    test_user = {
        "email": "tokensigntest@example.com",
        "password": "testpassword123"
    }
    await client.post("/api/auth/register", json=test_user)

    # Create a token with wrong secret
    invalid_token = jwt.encode(
        {"sub": 1, "email": test_user["email"]},
        "wrong-secret-key",
        algorithm=settings.JWT_ALGORITHM
    )

    # Try to access a protected endpoint with invalid token
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = await client.get("/api/tasks", headers=headers)
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_expired_token_fails(client: AsyncClient):
    """
    Test T104: Using an expired token should be rejected.

    This test ensures that expired JWT tokens are properly rejected.
    """
    # Create a valid user
    test_user = {
        "email": "expiredtoken@example.com",
        "password": "testpassword123"
    }
    await client.post("/api/auth/register", json=test_user)

    # Create an expired token (expired 1 hour ago)
    expired_payload = {
        "sub": 1,
        "email": test_user["email"],
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    expired_token = jwt.encode(
        expired_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    # Try to access a protected endpoint with expired token
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.get("/api/tasks", headers=headers)
    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_token_without_exp_fails(client: AsyncClient):
    """
    Test T104: Token without expiration claim should be rejected.

    This test ensures that tokens missing the 'exp' claim are rejected.
    """
    # Create a valid user
    test_user = {
        "email": "noexptoken@example.com",
        "password": "testpassword123"
    }
    await client.post("/api/auth/register", json=test_user)

    # Create a token without expiration
    token_no_exp = jwt.encode(
        {"sub": 1, "email": test_user["email"]},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    # Try to access a protected endpoint with token missing exp
    headers = {"Authorization": f"Bearer {token_no_exp}"}
    response = await client.get("/api/tasks", headers=headers)
    assert response.status_code == 401
    assert "detail" in response.json()