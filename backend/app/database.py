"""Database connection and session management."""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from typing import AsyncGenerator

from app.config import settings

# 1. Force String
db_url = str(settings.DATABASE_URL)

# 2. Force Async Driver Scheme
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# 3. Determine SSL requirement
# Use SSL for Neon/Vercel (detected by 'neon.tech' or 'vercel' in URL), disable for local
use_ssl = "neon.tech" in db_url or "vercel" in db_url or os.getenv("DB_SSL_REQUIRE", "false").lower() == "true"

# 4. Clean Query Params (Fixes 'sslmode' issue from before)
if "?" in db_url:
    base_url, query = db_url.split("?", 1)
    # Only keep params that asyncpg might support, or strip all to be safe if using connect_args
    db_url = base_url

# 5. Create Engine with conditional SSL
connect_args = {}
if use_ssl:
    connect_args["ssl"] = "require"  # Force SSL for Neon/Vercel

engine = create_async_engine(
    db_url,
    echo=settings.ENVIRONMENT == "local" if hasattr(settings, 'ENVIRONMENT') else settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args
)

# Base class for SQLAlchemy models
Base = declarative_base()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create tables on startup - needed for serverless environments
async def create_tables():
    """Create all database tables."""
    try:
        # Test database connection first
        async with engine.begin() as conn:
            # Just execute a simple query to test connection
            await conn.execute(text("SELECT 1"))
            print("Database connection successful")

        # Now try to create tables
        async with engine.begin() as conn:
            # Create all tables without checking first
            # This is safer for serverless where tables might exist
            await conn.run_sync(Base.metadata.create_all)
            print("Database tables ensured")
    except Exception as e:
        print(f"Warning: Database table creation failed: {e}")
        # Continue without failing - application might still work
        pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Database session

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
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
