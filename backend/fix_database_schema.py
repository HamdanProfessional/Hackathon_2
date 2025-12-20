"""Fix database schema by dropping all tables and recreating with migrations."""
import asyncio
from sqlalchemy import text
from app.database import engine, Base
from app.config import settings

async def fix_database_schema():
    """Drop all tables and recreate them using Alembic migrations."""
    print(f"Connecting to database: {settings.DATABASE_URL}")

    # Drop all tables created by create_all
    print("\n1. Dropping all existing tables...")
    try:
        async with engine.begin() as conn:
            # Drop all tables in the correct order (children first)
            # Note: We'll drop alembic version last
            tables_to_drop = [
                'taskassignments',
                'tasks',
                'conversations',
                'messages',
                'user_sessions',
                'users'
            ]

            for table in tables_to_drop:
                try:
                    await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"   [OK] Dropped table: {table}")
                except Exception as e:
                    print(f"   [WARN] Table {table} may not exist: {e}")

            # Also drop alembic version table
            try:
                await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
                print(f"   [OK] Dropped table: alembic_version")
            except Exception as e:
                print(f"   [WARN] alembic_version table may not exist: {e}")

        print("\n2. All tables dropped successfully!")

    except Exception as e:
        print(f"\n[ERROR] Error dropping tables: {e}")
        return False

    # Now run the final migration that recreates all tables with correct schema
    print("\n3. Running final migration to recreate tables with correct schema...")
    try:
        import subprocess
        import sys

        # Run alembic stamp 0 to reset migration state
        print("   Resetting migration state...")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "stamp", "0"],
            capture_output=True,
            text=True,
            cwd="."
        )

        if result.returncode != 0:
            print(f"   [WARN] Could not reset migration state: {result.stderr}")

        # Run the final migration that recreates all tables
        print("   Running final migration (69ef5db393b3)...")
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "69ef5db393b3"],
            capture_output=True,
            text=True,
            cwd="."
        )

        if result.returncode == 0:
            print("   [OK] Migration completed successfully!")
            if result.stdout:
                print(f"   Output: {result.stdout}")
        else:
            print(f"   [ERROR] Migration failed:")
            print(f"   Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"   [ERROR] Error running migration: {e}")
        return False

    # Verify the schema
    print("\n4. Verifying database schema...")
    try:
        async with engine.begin() as conn:
            # Check users table
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            print("\n   Users table columns:")
            for col in columns:
                print(f"     - {col[0]}: {col[1]} (nullable: {col[2]})")

            # Check that name column exists
            has_name = any(col[0] == 'name' for col in columns)
            if has_name:
                print("\n   [OK] 'name' column exists in users table!")
            else:
                print("\n   [ERROR] 'name' column is missing from users table!")
                return False

    except Exception as e:
        print(f"\n   [ERROR] Error verifying schema: {e}")
        return False

    print("\n[SUCCESS] Database schema fixed successfully!")
    print("   The database now has the correct schema with 'name' field in users table.")
    return True

if __name__ == "__main__":
    asyncio.run(fix_database_schema())