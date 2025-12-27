"""Database connection and session management for notification service."""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from typing import AsyncGenerator

from app.config import settings

# Import the Base from the backend models
# The notification service shares the same database schema
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def get_database_url() -> str:
    """
    Get and format the database URL for async PostgreSQL.

    Returns:
        str: Async PostgreSQL database URL
    """
    db_url = str(settings.DATABASE_URL)

    # Force Async Driver Scheme
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Determine SSL requirement
    use_ssl = ("neon.tech" in db_url or "vercel" in db_url or
               os.getenv("DB_SSL_REQUIRE", "false").lower() == "true")

    # Clean Query Params
    if "?" in db_url:
        base_url, _ = db_url.split("?", 1)
        db_url = base_url

    return db_url, use_ssl


# Create engine
db_url, use_ssl = get_database_url()

connect_args = {}
if use_ssl:
    connect_args["ssl"] = "require"

engine = create_async_engine(
    db_url,
    echo=settings.ENVIRONMENT == "local",
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def test_database_connection() -> bool:
    """
    Test database connection.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("[Notification Service] Database connection successful")
        return True
    except Exception as e:
        print(f"[Notification Service] Database connection failed: {e}")
        return False
