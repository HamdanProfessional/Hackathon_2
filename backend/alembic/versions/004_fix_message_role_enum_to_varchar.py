"""Fix message_role ENUM to VARCHAR(20) with CHECK constraint

Revision ID: 004
Revises: 5e990c3ddfe4
Create Date: 2025-12-22

This migration fixes a schema mismatch between production and local databases:
- Production (Vercel/Neon): Has message_role ENUM type
- Local (SQLite/PostgreSQL): Has VARCHAR(20) with CHECK constraint
- SQLAlchemy Model: Expects VARCHAR(20)

The migration:
1. Detects if message_role ENUM type exists in the database
2. If it exists:
   - Converts messages.role column from ENUM to VARCHAR(20)
   - Drops the message_role ENUM type
   - Ensures CHECK constraint is in place
3. Is idempotent - safe to run multiple times on both production and local

This resolves the error:
"column 'role' is of type message_role but expression is of type character varying"
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '5e990c3ddfe4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert message_role ENUM to VARCHAR(20) with CHECK constraint.

    This migration is idempotent - it checks if the ENUM exists before attempting conversion.
    Safe to run on:
    - Production databases with message_role ENUM
    - Local databases already using VARCHAR(20)
    """

    # Step 1: Check if message_role ENUM type exists
    connection = op.get_bind()

    # Query pg_type to see if message_role enum exists
    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1
            FROM pg_type
            WHERE typname = 'message_role'
        );
    """))
    enum_exists = result.scalar()

    if enum_exists:
        print("[INFO] Detected message_role ENUM type - converting to VARCHAR(20)")

        # Step 2: Alter the column type from ENUM to VARCHAR(20)
        # Using USING clause to safely cast the ENUM values to text/varchar
        op.execute("""
            ALTER TABLE messages
            ALTER COLUMN role TYPE VARCHAR(20)
            USING role::text;
        """)
        print("[INFO] Converted messages.role from ENUM to VARCHAR(20)")

        # Step 3: Ensure CHECK constraint exists (may already exist, so use IF NOT EXISTS pattern)
        # First check if constraint exists
        constraint_result = connection.execute(sa.text("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.constraint_column_usage
                WHERE table_name = 'messages'
                AND constraint_name = 'check_role_values'
            );
        """))
        constraint_exists = constraint_result.scalar()

        if not constraint_exists:
            op.create_check_constraint(
                'check_role_values',
                'messages',
                "role IN ('user', 'assistant', 'system', 'tool')"
            )
            print("[INFO] Added CHECK constraint: check_role_values")
        else:
            print("[INFO] CHECK constraint already exists")

        # Step 4: Drop the message_role ENUM type (now unused)
        op.execute("DROP TYPE message_role;")
        print("[INFO] Dropped message_role ENUM type")

        print("\n[SUCCESS] Migration complete: messages.role is now VARCHAR(20) with CHECK constraint")
    else:
        print("[INFO] No message_role ENUM detected - column is already VARCHAR(20)")
        print("[INFO] Verifying CHECK constraint exists...")

        # Ensure CHECK constraint exists even if ENUM didn't exist
        constraint_result = connection.execute(sa.text("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.constraint_column_usage
                WHERE table_name = 'messages'
                AND constraint_name = 'check_role_values'
            );
        """))
        constraint_exists = constraint_result.scalar()

        if not constraint_exists:
            op.create_check_constraint(
                'check_role_values',
                'messages',
                "role IN ('user', 'assistant', 'system', 'tool')"
            )
            print("[INFO] Added CHECK constraint: check_role_values")
        else:
            print("[INFO] CHECK constraint already exists")

        print("\n[SUCCESS] Migration complete: Schema already correct")


def downgrade() -> None:
    """Downgrade from VARCHAR(20) to message_role ENUM.

    WARNING: This is rarely needed and assumes you want to revert to ENUM.
    Only use if you need to match a specific production schema that requires ENUM.
    """

    # Step 1: Create the message_role ENUM type if it doesn't exist
    connection = op.get_bind()

    result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1
            FROM pg_type
            WHERE typname = 'message_role'
        );
    """))
    enum_exists = result.scalar()

    if not enum_exists:
        # Create the ENUM type
        op.execute("""
            CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system', 'tool');
        """)
        print("[INFO] Created message_role ENUM type")

    # Step 2: Drop the CHECK constraint if it exists
    constraint_result = connection.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.constraint_column_usage
            WHERE table_name = 'messages'
            AND constraint_name = 'check_role_values'
        );
    """))
    constraint_exists = constraint_result.scalar()

    if constraint_exists:
        op.drop_constraint('check_role_values', 'messages', type_='check')
        print("[INFO] Dropped CHECK constraint")

    # Step 3: Alter column back to ENUM type
    op.execute("""
        ALTER TABLE messages
        ALTER COLUMN role TYPE message_role
        USING role::text::message_role;
    """)
    print("[INFO] Converted messages.role from VARCHAR(20) to message_role ENUM")

    print("\n[SUCCESS] Downgrade complete: messages.role is now message_role ENUM")
