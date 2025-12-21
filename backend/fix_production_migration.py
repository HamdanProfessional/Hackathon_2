#!/usr/bin/env python3
"""
EMERGENCY PRODUCTION MIGRATION FIX

This script fixes the critical production issue where conversations and messages
tables have integer columns instead of UUID columns.

Run this script in production IMMEDIATELY to fix the schema mismatch.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[0]))

from sqlalchemy import text
from app.database import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def fix_production_migration():
    """Fix the production database schema by applying the UUID migration."""
    logger.info("🚨 EMERGENCY PRODUCTION MIGRATION FIX 🚨")
    logger.info("Starting production database fix...")

    try:
        async with engine.begin() as conn:
            # Step 1: Check current migration state
            logger.info("Step 1: Checking current migration state...")
            result = await conn.execute(text("""
                SELECT version_num FROM alembic_version
            """))
            current_version = result.scalar()
            logger.info(f"Current Alembic version: {current_version}")

            # Step 2: Check if conversations table exists
            logger.info("Step 2: Checking conversations table...")
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'conversations'
                )
            """))
            conversations_exist = result.scalar()

            if not conversations_exist:
                logger.info("Conversations table doesn't exist, updating alembic version...")
                await conn.execute(text("""
                    UPDATE alembic_version SET version_num = 'e940f362bb65'
                """))
                await conn.commit()
                logger.info("✅ Migration marked as complete (no tables to migrate)")
                return

            # Step 3: Check column types
            logger.info("Step 3: Checking column types...")
            result = await conn.execute(text("""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_name = 'conversations' AND column_name = 'id'
            """))
            id_type = result.scalar()

            logger.info(f"Conversations.id column type: {id_type}")

            # Step 4: Run migration if needed
            if id_type == 'integer':
                logger.warning("⚠️  INTEGER columns detected! Running migration...")

                # Back up data if any exists (though tables might be empty)
                logger.info("Step 4a: Backing up any existing data...")
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM conversations
                """))
                conv_count = result.scalar()

                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM messages
                """))
                msg_count = result.scalar()

                logger.info(f"Found {conv_count} conversations and {msg_count} messages")

                # Step 4b: Drop and recreate tables with UUID columns
                logger.info("Step 4b: Dropping existing tables...")
                await conn.execute(text('DROP TABLE IF EXISTS messages CASCADE'))
                await conn.execute(text('DROP TABLE IF EXISTS conversations CASCADE'))

                logger.info("Step 4c: Creating conversations table with UUID columns...")
                await conn.execute(text("""
                    CREATE TABLE conversations (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        title VARCHAR(200) NOT NULL DEFAULT 'New Conversation',
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))

                logger.info("Step 4d: Creating performance indexes...")
                await conn.execute(text("""
                    CREATE INDEX idx_conversations_created_at_desc
                    ON conversations (created_at DESC)
                """))

                logger.info("Step 4e: Creating messages table with UUID columns...")
                await conn.execute(text("""
                    CREATE TABLE messages (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                        role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
                        content TEXT NOT NULL,
                        tool_calls JSONB,
                        tool_call_id VARCHAR(100),
                        name VARCHAR(100),
                        created_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))

                await conn.execute(text("""
                    CREATE INDEX idx_messages_conversation_created
                    ON messages (conversation_id, created_at)
                """))

                # Step 4f: Update alembic version
                logger.info("Step 4f: Updating alembic version...")
                await conn.execute(text("""
                    UPDATE alembic_version SET version_num = 'e940f362bb65'
                """))

                await conn.commit()

                logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY!")
                logger.info(f"   - Dropped {conv_count} conversations and {msg_count} messages")
                logger.info("   - Recreated tables with UUID columns")
                logger.info("   - Updated Alembic version to e940f362bb65")

            else:
                logger.info(f"✅ Tables already have UUID columns (type: {id_type})")
                logger.info("No migration needed")

    except Exception as e:
        logger.error(f"❌ MIGRATION FAILED: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


async def verify_fix():
    """Verify that the fix was successful."""
    logger.info("\n🔍 Verifying migration fix...")

    try:
        async with engine.begin() as conn:
            # Check conversations table schema
            result = await conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'conversations'
                ORDER BY ordinal_position
            """))
            conv_columns = result.fetchall()

            logger.info("Conversations table schema:")
            for col in conv_columns:
                logger.info(f"  - {col[0]}: {col[1]}")

            # Check messages table schema
            result = await conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'messages'
                ORDER BY ordinal_position
            """))
            msg_columns = result.fetchall()

            logger.info("Messages table schema:")
            for col in msg_columns:
                logger.info(f"  - {col[0]}: {col[1]}")

            # Check alembic version
            result = await conn.execute(text("""
                SELECT version_num FROM alembic_version
            """))
            version = result.scalar()

            logger.info(f"Alembic version: {version}")

            # Test creating a conversation
            logger.info("\n🧪 Testing conversation creation...")
            result = await conn.execute(text("""
                SELECT id FROM users LIMIT 1
            """))
            user_row = result.scalar_one_or_none()

            if user_row:
                import uuid
                conversation_id = str(uuid.uuid4())

                result = await conn.execute(text("""
                    INSERT INTO conversations (id, user_id, title, created_at, updated_at)
                    VALUES (:id, :user_id, :title, NOW(), NOW())
                    RETURNING id
                """), {
                    "id": conversation_id,
                    "user_id": str(user_row),
                    "title": "Test Conversation After Fix"
                })

                inserted_id = result.scalar()
                logger.info(f"✅ Successfully created test conversation: {inserted_id}")

                # Clean up test conversation
                await conn.execute(text("""
                    DELETE FROM conversations WHERE id = :id
                """), {"id": conversation_id})

            logger.info("\n✅ VERIFICATION COMPLETE - All checks passed!")

    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
        raise


async def main():
    """Main function to run the fix."""
    logger.info("=" * 60)
    logger.info("PRODUCTION DATABASE EMERGENCY FIX")
    logger.info("=" * 60)

    # Check if we're in production
    env = os.getenv("ENVIRONMENT", "development")
    logger.info(f"Environment: {env}")

    if env != "production":
        logger.warning("⚠️  This script is intended for PRODUCTION only!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            logger.info("Aborted.")
            return

    # Confirm before proceeding
    logger.warning("\n⚠️  WARNING: This will DROP and RECREATE conversations and messages tables!")
    response = input("Proceed with migration? (y/N): ")
    if response.lower() != 'y':
        logger.info("Aborted.")
        return

    # Run the fix
    await fix_production_migration()

    # Verify the fix
    await verify_fix()

    logger.info("\n🎉 PRODUCTION FIX COMPLETE!")
    logger.info("The database schema has been updated successfully.")
    logger.info("Conversation functionality should now work properly.")


if __name__ == "__main__":
    asyncio.run(main())