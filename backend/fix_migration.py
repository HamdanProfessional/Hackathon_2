"""Fix broken alembic migration state."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_3DbyqCvjPnN7@ep-mute-hill-agz5np87-pooler.c-2.eu-central-1.aws.neon.tech/neondb?ssl=require"

async def fix_migration():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Delete broken revision
        await conn.execute(text("DELETE FROM alembic_version WHERE version_num LIKE 'b162%'"))
        # Set to known good revision (006 - subtasks table)
        await conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('006')"))
        result = await conn.execute(text("SELECT version_num FROM alembic_version"))
        print(f"Fixed! Current version: {result.scalar()}")
    await engine.dispose()

asyncio.run(fix_migration())
