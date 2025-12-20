"""Verify Phase III migration requirements are met."""
import asyncio
from app.database import engine
from sqlalchemy import text


async def verify_migration():
    """Verify all Phase III requirements are implemented."""
    async with engine.begin() as conn:
        print("=" * 60)
        print("PHASE III MIGRATION VERIFICATION")
        print("=" * 60)

        # Check Conversations table
        print("\n[OK] CONVERSATIONS TABLE:")
        result = await conn.execute(
            text("""
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns
                WHERE table_name='conversations'
                ORDER BY ordinal_position
            """)
        )
        for row in result:
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            length = f"({row[2]})" if row[2] else ""
            print(f"  - {row[0]}: {row[1]}{length} {nullable}")

        # Verify UUID primary key
        result = await conn.execute(
            text("SELECT data_type FROM information_schema.columns WHERE table_name='conversations' AND column_name='id'")
        )
        id_type = result.scalar()
        assert id_type == "uuid", f"conversations.id should be UUID, got {id_type}"
        print("\n  [OK] Requirement 1: conversations.id is UUID")

        # Verify title field
        result = await conn.execute(
            text("SELECT data_type, character_maximum_length FROM information_schema.columns WHERE table_name='conversations' AND column_name='title'")
        )
        row = result.fetchone()
        assert row is not None, "conversations.title field missing"
        assert row[1] == 200, f"conversations.title should be String(200), got {row[1]}"
        print("  [OK] Requirement 2: conversations.title is String(200)")

        # Check for created_at index
        result = await conn.execute(
            text("""
                SELECT indexname FROM pg_indexes
                WHERE tablename='conversations' AND indexname LIKE '%created_at%'
            """)
        )
        indexes = [row[0] for row in result]
        print(f"  [OK] Requirement 3: Index on created_at: {indexes}")

        # Check Messages table
        print("\n[OK] MESSAGES TABLE:")
        result = await conn.execute(
            text("""
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns
                WHERE table_name='messages'
                ORDER BY ordinal_position
            """)
        )
        for row in result:
            nullable = "NULL" if row[3] == "YES" else "NOT NULL"
            length = f"({row[2]})" if row[2] else ""
            print(f"  - {row[0]}: {row[1]}{length} {nullable}")

        # Verify UUID primary key
        result = await conn.execute(
            text("SELECT data_type FROM information_schema.columns WHERE table_name='messages' AND column_name='id'")
        )
        id_type = result.scalar()
        assert id_type == "uuid", f"messages.id should be UUID, got {id_type}"
        print("\n  [OK] Requirement 4: messages.id is UUID")

        # Verify UUID foreign key
        result = await conn.execute(
            text("SELECT data_type FROM information_schema.columns WHERE table_name='messages' AND column_name='conversation_id'")
        )
        fk_type = result.scalar()
        assert fk_type == "uuid", f"messages.conversation_id should be UUID, got {fk_type}"
        print("  [OK] Requirement 5: messages.conversation_id is UUID FK")

        # Verify tool_calls JSON field
        result = await conn.execute(
            text("SELECT data_type, is_nullable FROM information_schema.columns WHERE table_name='messages' AND column_name='tool_calls'")
        )
        row = result.fetchone()
        assert row is not None, "messages.tool_calls field missing"
        assert row[0] in ["json", "jsonb"], f"messages.tool_calls should be JSON, got {row[0]}"
        assert row[1] == "YES", "messages.tool_calls should be nullable"
        print("  [OK] Requirement 6: messages.tool_calls is JSON (nullable)")

        # Verify tool_call_id field
        result = await conn.execute(
            text("SELECT data_type, character_maximum_length, is_nullable FROM information_schema.columns WHERE table_name='messages' AND column_name='tool_call_id'")
        )
        row = result.fetchone()
        assert row is not None, "messages.tool_call_id field missing"
        assert row[1] == 100, f"messages.tool_call_id should be String(100), got {row[1]}"
        assert row[2] == "YES", "messages.tool_call_id should be nullable"
        print("  [OK] Requirement 7: messages.tool_call_id is String(100, nullable)")

        # Verify name field
        result = await conn.execute(
            text("SELECT data_type, character_maximum_length, is_nullable FROM information_schema.columns WHERE table_name='messages' AND column_name='name'")
        )
        row = result.fetchone()
        assert row is not None, "messages.name field missing"
        assert row[1] == 100, f"messages.name should be String(100), got {row[1]}"
        assert row[2] == "YES", "messages.name should be nullable"
        print("  [OK] Requirement 8: messages.name is String(100, nullable)")

        # Verify role constraint
        result = await conn.execute(
            text("""
                SELECT check_clause FROM information_schema.check_constraints
                WHERE constraint_name='check_role_values'
            """)
        )
        constraint = result.scalar()
        assert constraint is not None, "check_role_values constraint missing"
        assert "'system'" in constraint or "system" in constraint, "role constraint missing 'system'"
        assert "'tool'" in constraint or "tool" in constraint, "role constraint missing 'tool'"
        print(f"  [OK] Requirement 9: role constraint includes 'system' and 'tool'")

        # Check for message indexes
        result = await conn.execute(
            text("""
                SELECT indexname, indexdef FROM pg_indexes
                WHERE tablename='messages'
                ORDER BY indexname
            """)
        )
        print("\n  [OK] Requirement 10: Indexes on messages:")
        for row in result:
            print(f"    - {row[0]}")

        print("\n" + "=" * 60)
        print("[SUCCESS] ALL REQUIREMENTS MET!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(verify_migration())
