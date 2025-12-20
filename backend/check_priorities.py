"""Check the priorities in the database."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_priorities():
    """Check priorities table."""
    db_url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')
    conn = await asyncpg.connect(db_url)

    print("Checking priorities table...")
    rows = await conn.fetch("SELECT * FROM priorities ORDER BY id")

    if rows:
        print("\nPriorities found:")
        for row in rows:
            print(f"  ID: {row['id']}, Name: {row['name']}, Level: {row['level']}")
    else:
        print("No priorities found in database!")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_priorities())