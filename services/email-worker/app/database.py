"""Database configuration for email worker."""
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session() as session:
        yield session


async def init_db():
    """Initialize database connection."""
    try:
        async with engine.begin() as conn:
            # Test connection
            await conn.execute("SELECT 1")
        print("Database connection initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")


async def close_db():
    """Close database connection."""
    await engine.dispose()
    print("Database connection closed")
