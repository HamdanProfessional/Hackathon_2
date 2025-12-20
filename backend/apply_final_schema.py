"""Apply final database schema directly without intermediate migrations."""
import asyncio
from sqlalchemy import text
from app.database import engine
from app.config import settings

async def apply_final_schema():
    """Apply the final database schema directly."""
    print(f"Connecting to database: {settings.DATABASE_URL}")

    try:
        async with engine.begin() as conn:
            # Enable UUID extension
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            print("   [OK] UUID extension enabled")

            # Create users table with UUID primary key
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    password_hash VARCHAR(255),  -- For compatibility
                    preferences JSON,
                    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
                    CONSTRAINT check_email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
                )
            """))
            print("   [OK] Users table created")

            # Create indexes for users
            await conn.execute(text('CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)'))
            print("   [OK] Users indexes created")

            # Create tasks table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    priority VARCHAR(10) DEFAULT 'MEDIUM' NOT NULL,
                    status VARCHAR(20) DEFAULT 'active' NOT NULL,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    due_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
                    completed_at TIMESTAMP,
                    CONSTRAINT check_priority_values CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH')),
                    CONSTRAINT check_status_values CHECK (status IN ('active', 'completed'))
                )
            """))
            print("   [OK] Tasks table created")

            # Create indexes for tasks
            indexes = [
                'CREATE INDEX IF NOT EXISTS ix_tasks_id ON tasks (id)',
                'CREATE INDEX IF NOT EXISTS ix_tasks_user_id ON tasks (user_id)',
                'CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks (status)',
                'CREATE INDEX IF NOT EXISTS ix_tasks_priority ON tasks (priority)',
                'CREATE INDEX IF NOT EXISTS ix_tasks_created_at ON tasks (created_at)',
                'CREATE INDEX IF NOT EXISTS ix_tasks_due_date ON tasks (due_date)',
                'CREATE INDEX IF NOT EXISTS ix_tasks_user_status ON tasks (user_id, status)'
            ]
            for idx in indexes:
                await conn.execute(text(idx))
            print("   [OK] Tasks indexes created")

            # Create conversations table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                    updated_at TIMESTAMP DEFAULT NOW() NOT NULL
                )
            """))
            print("   [OK] Conversations table created")

            # Create indexes for conversations
            indexes = [
                'CREATE INDEX IF NOT EXISTS ix_conversations_id ON conversations (id)',
                'CREATE INDEX IF NOT EXISTS ix_conversations_user_id ON conversations (user_id)',
                'CREATE INDEX IF NOT EXISTS ix_conversations_updated_at ON conversations (updated_at)'
            ]
            for idx in indexes:
                await conn.execute(text(idx))
            print("   [OK] Conversations indexes created")

            # Create messages table
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW() NOT NULL
                )
            """))
            print("   [OK] Messages table created")

            # Create indexes for messages
            indexes = [
                'CREATE INDEX IF NOT EXISTS ix_messages_id ON messages (id)',
                'CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id)',
                'CREATE INDEX IF NOT EXISTS ix_messages_created_at ON messages (created_at)'
            ]
            for idx in indexes:
                await conn.execute(text(idx))
            print("   [OK] Messages indexes created")

            # Create alembic version table and mark as current
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL PRIMARY KEY
                )
            """))

            # Mark the final migration as applied
            await conn.execute(text("""
                INSERT INTO alembic_version (version_num)
                VALUES ('69ef5db393b3')
                ON CONFLICT (version_num) DO NOTHING
            """))
            print("   [OK] Migration state marked as current")

        print("\n[SUCCESS] Database schema created successfully!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Error creating schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(apply_final_schema())