"""Test database connection directly."""
import asyncio
from app.config import settings
from app.database import engine
from sqlalchemy import text

async def test_db():
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Database connection successful!")
            print(f"Result: {result.scalar()}")
    except Exception as e:
        print(f"Database connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())