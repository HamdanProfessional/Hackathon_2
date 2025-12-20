"""Check what tables exist in the database."""
import asyncio
from app.database import engine
from sqlalchemy import text


async def check_tables():
    """Check existing tables in the database."""
    async with engine.begin() as conn:
        # Get all tables
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        )
        tables = [row[0] for row in result]

        print("Existing tables:")
        for table in tables:
            print(f"  - {table}")

        # Check conversations table structure
        if 'conversations' in tables:
            print("\nConversations table structure:")
            result = await conn.execute(
                text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='conversations' ORDER BY ordinal_position")
            )
            for row in result:
                print(f"  {row[0]}: {row[1]} (nullable={row[2]})")

        # Check messages table structure
        if 'messages' in tables:
            print("\nMessages table structure:")
            result = await conn.execute(
                text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='messages' ORDER BY ordinal_position")
            )
            for row in result:
                print(f"  {row[0]}: {row[1]} (nullable={row[2]})")


if __name__ == "__main__":
    asyncio.run(check_tables())
