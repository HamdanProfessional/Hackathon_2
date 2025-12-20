"""Recreate database schema from scratch."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def recreate_schema():
    """Drop and recreate all tables with correct schema."""
    # Use asyncpg directly for raw SQL
    db_url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')
    conn = await asyncpg.connect(db_url)

    print("Dropping all tables...")
    # Drop all tables in correct order (child tables first)
    await conn.execute("DROP TABLE IF EXISTS messages CASCADE")
    await conn.execute("DROP TABLE IF EXISTS conversations CASCADE")
    await conn.execute("DROP TABLE IF EXISTS tasks CASCADE")
    await conn.execute("DROP TABLE IF EXISTS priorities CASCADE")
    await conn.execute("DROP TABLE IF EXISTS users CASCADE")
    await conn.execute("DROP TABLE IF EXISTS alembic_version CASCADE")

    print("Creating UUID extension...")
    await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

    print("Creating users table...")
    await conn.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            preferences JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    print("Creating priorities table...")
    await conn.execute("""
        CREATE TABLE priorities (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL,
            level INTEGER NOT NULL,
            color VARCHAR(7)
        )
    """)

    print("Inserting default priorities...")
    await conn.execute("""
        INSERT INTO priorities (name, level, color) VALUES
        ('LOW', 1, '#22c55e'),
        ('MEDIUM', 2, '#f59e0b'),
        ('HIGH', 3, '#ef4444')
    """)

    print("Creating tasks table...")
    await conn.execute("""
        CREATE TABLE tasks (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            priority_id INTEGER REFERENCES priorities(id),
            title VARCHAR(500) NOT NULL,
            description TEXT DEFAULT '',
            completed BOOLEAN DEFAULT FALSE,
            due_date DATE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_recurring BOOLEAN DEFAULT FALSE,
            recurrence_pattern VARCHAR(100)
        )
    """)

    print("Creating indexes...")
    await conn.execute("CREATE INDEX idx_tasks_user_id ON tasks(user_id)")
    await conn.execute("CREATE INDEX idx_tasks_completed ON tasks(completed)")
    await conn.execute("CREATE INDEX idx_tasks_due_date ON tasks(due_date)")
    await conn.execute("CREATE INDEX idx_tasks_created_at ON tasks(created_at)")

    print("Creating conversations table...")
    await conn.execute("""
        CREATE TABLE conversations (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    print("Creating messages table...")
    await conn.execute("""
        CREATE TABLE messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    print("Creating more indexes...")
    await conn.execute("CREATE INDEX idx_messages_conversation_id ON messages(conversation_id)")
    await conn.execute("CREATE INDEX idx_conversations_user_id ON conversations(user_id)")

    # Create alembic version table
    print("Creating alembic version table...")
    await conn.execute("""
        CREATE TABLE alembic_version (
            version_num VARCHAR(32) NOT NULL
        )
    """)

    # Mark as up to date with latest migration
    await conn.execute("""
        INSERT INTO alembic_version (version_num) VALUES ('69ef5db393b3')
    """)

    print("Granting permissions...")
    # Skip permission grants for Neon - they're not needed

    await conn.close()
    print("\nDatabase schema recreated successfully!")

if __name__ == "__main__":
    asyncio.run(recreate_schema())