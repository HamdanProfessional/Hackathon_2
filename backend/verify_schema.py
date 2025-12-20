"""Verify database schema matches models."""

import asyncio
import sys
from sqlalchemy import text
from app.database import AsyncSessionLocal


async def verify_schema():
    """Verify that the database schema matches the models."""
    print("Verifying database schema...")

    async with AsyncSessionLocal() as session:
        # Check users table
        print("\n=== Users Table ===")
        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        users_schema = result.fetchall()
        for row in users_schema:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")

        # Check conversations table
        print("\n=== Conversations Table ===")
        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'conversations'
            ORDER BY ordinal_position
        """))
        conv_schema = result.fetchall()
        for row in conv_schema:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")

        # Check messages table
        print("\n=== Messages Table ===")
        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'messages'
            ORDER BY ordinal_position
        """))
        msg_schema = result.fetchall()
        for row in msg_schema:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")

        # Check if foreign key exists
        print("\n=== Foreign Key Constraints ===")
        result = await session.execute(text("""
            SELECT
                tc.table_name,
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name IN ('conversations', 'messages', 'tasks')
        """))
        fks = result.fetchall()
        for fk in fks:
            print(f"  {fk[0]}.{fk[3]} -> {fk[4]}.{fk[5]} ({fk[2]})")

        # Check if triggers exist
        print("\n=== Triggers ===")
        result = await session.execute(text("""
            SELECT trigger_name, event_manipulation, event_object_table
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            ORDER BY event_object_table, trigger_name
        """))
        triggers = result.fetchall()
        for trig in triggers:
            print(f"  {trig[2]}: {trig[0]} ({trig[1]})")

        # Validate critical points
        print("\n=== Validation ===")

        # Check if users.id is UUID
        user_id_type = None
        for row in users_schema:
            if row[0] == 'id':
                user_id_type = row[1]
                break

        if user_id_type == 'uuid':
            print("✓ users.id is UUID type")
        else:
            print(f"✗ users.id is {user_id_type}, should be uuid")

        # Check if conversations.user_id is UUID
        conv_user_id_type = None
        for row in conv_schema:
            if row[0] == 'user_id':
                conv_user_id_type = row[1]
                break

        if conv_user_id_type == 'uuid':
            print("✓ conversations.user_id is UUID type")
        else:
            print(f"✗ conversations.user_id is {conv_user_id_type}, should be uuid")

        # Check for foreign key constraints
        has_conversations_fk = any(
            fk[0] == 'conversations' and fk[3] == 'user_id' and fk[4] == 'users' and fk[5] == 'id'
            for fk in fks
        )

        if has_conversations_fk:
            print("✓ conversations.user_id foreign key to users.id exists")
        else:
            print("✗ conversations.user_id foreign key to users.id missing")

        # Summary
        print("\n=== Summary ===")
        if user_id_type == 'uuid' and conv_user_id_type == 'uuid' and has_conversations_fk:
            print("✓ Database schema is correctly configured for Phase 3!")
            return True
        else:
            print("✗ Database schema needs manual fixing")
            return False


if __name__ == "__main__":
    success = asyncio.run(verify_schema())
    sys.exit(0 if success else 1)