"""Setup test database tables."""
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.test"), override=True)
os.environ["TESTING"] = "true"

from app.database import Base
from app.models.user import User
from app.models.task import Task, Priority
from app.models.recurring_task import RecurringTask
from app.models.task_event_log import TaskEventLog
from app.models.conversation import Conversation
from app.models.message import Message
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def setup_test_db():
    """Create test database tables."""
    engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5433/test_db")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Seed priorities
        insert_sql = """INSERT INTO priorities (id, name, level, color) VALUES
            (1, 'Low', 1, 'green'),
            (2, 'Medium', 2, 'yellow'),
            (3, 'High', 3, 'red')
            ON CONFLICT (id) DO NOTHING"""
        await conn.execute(text(insert_sql))
        print("Tables created and priorities seeded")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(setup_test_db())
