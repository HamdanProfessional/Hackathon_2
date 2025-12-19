"""Pytest configuration and fixtures."""
import asyncio
import os
import sys

# Set test environment variable as early as possible
os.environ["TESTING"] = "true"

# Now import the app to ensure it picks up test settings
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import NullPool
from app.main import app
from app.database import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker


# Override database dependency for testing
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Use SQLite file database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="session")
async def test_db_session_factory():
    """Create a test database session factory."""
    # Create test engine with NullPool to prevent connection holding
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    # Import Base and drop/create all tables for fresh test database
    from app.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create test session factory
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    yield async_session

    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_db_session_factory) -> AsyncClient:
    """Create a test client with database override."""
    from app.main import app

    # Override the database dependency
    async def override_get_db():
        async with test_db_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Create ASGI transport for httpx
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def get_db_override(test_db_session_factory):
    """Return a function that can be used to get database sessions in tests."""
    async def _get_db():
        async with test_db_session_factory() as session:
            yield session
    return _get_db


@pytest.fixture
def test_user_data():
    """Test user data for registration."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
    }


@pytest.fixture
def another_test_user_data():
    """Another test user data for registration tests."""
    return {
        "email": "another@example.com",
        "password": "anotherpassword123",
    }