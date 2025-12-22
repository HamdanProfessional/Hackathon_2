from logging.config import fileConfig
import asyncio
import sys
import logging
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import create_engine

from alembic import context

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.database import Base

# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User  # Phase II - Authentication
from app.models.task import Task  # Phase II - Task CRUD
from app.models.conversation import Conversation  # Phase III - AI Chatbot
from app.models.message import Message  # Phase III - AI Chatbot

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url from environment
# Ensure it uses asyncpg for async migrations
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    # asyncpg doesn't accept sslmode in URL, so we'll handle it in the engine config
    base_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    # Remove query parameters that asyncpg doesn't support
    # Split URL at '?' to handle query string
    if "?" in base_url:
        base_url = base_url.split("?")[0] + "?ssl=require"
elif db_url.startswith("postgresql+asyncpg://"):
    base_url = db_url
else:
    base_url = db_url

config.set_main_option("sqlalchemy.url", base_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (sync version, fallback for async context)."""
    # Create sync engine
    configuration = config.get_section(config.config_ini_section, {})
    # Add SSL configuration for psycopg2
    configuration["connect_args"] = {"sslmode": "require"}

    # Convert asyncpg URL to psycopg2 URL for sync engine
    db_url = configuration.get("sqlalchemy.url", "")
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "", 1)
        configuration["sqlalchemy.url"] = db_url

    connectable = create_engine(
        configuration,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


def run_migrations_sync() -> None:
    """Run migrations in 'online' mode using sync engine (fallback for async context)."""
    logger = logging.getLogger("alembic.env")
    logger.info("Running migrations in sync mode (fallback for async context)")
    run_migrations_online()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    # Create async engine
    configuration = config.get_section(config.config_ini_section, {})
    # Add SSL configuration for asyncpg
    configuration["connect_args"] = {"ssl": True}

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    """Execute migrations with the provided connection (works for both sync and async)."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Check if we're already in an event loop
    try:
        loop = asyncio.get_running_loop()
        # If we get here, we're in an async context
        # We cannot use asyncio.run() inside an existing loop
        # So we'll run the sync version instead
        logger = logging.getLogger("alembic.env")
        logger.warning("Running migrations in sync mode due to existing event loop")
        run_migrations_sync()
    except RuntimeError:
        # No running loop, safe to use asyncio.run()
        asyncio.run(run_async_migrations())
