"""Fix conversations table user_id to be UUID instead of integer

Revision ID: 002
Revises: 001
Create Date: 2025-12-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix user_id column to be UUID type to match the model."""

    # Drop existing indexes on user_id
    op.drop_index('ix_conversations_user_id', table_name='conversations')

    # Drop foreign key constraint
    op.drop_constraint('conversations_user_id_fkey', table_name='conversations', type_='foreignkey')

    # Change user_id column from integer to UUID
    # Using batch operations for PostgreSQL
    op.execute('''
        ALTER TABLE conversations
        ALTER COLUMN user_id TYPE UUID USING user_id::text::UUID
    ''')

    # Re-add foreign key constraint with UUID type
    op.create_foreign_key(
        'conversations_user_id_fkey',
        'conversations',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Re-create index on user_id
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])


def downgrade() -> None:
    """Revert user_id column back to integer type."""

    # Drop index on user_id
    op.drop_index('ix_conversations_user_id', table_name='conversations')

    # Drop foreign key constraint
    op.drop_constraint('conversations_user_id_fkey', table_name='conversations', type_='foreignkey')

    # Revert user_id column to integer
    op.execute('''
        ALTER TABLE conversations
        ALTER COLUMN user_id TYPE INTEGER USING user_id::text::INTEGER
    ''')

    # Re-add foreign key constraint with integer type
    op.create_foreign_key(
        'conversations_user_id_fkey',
        'conversations',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Re-create index on user_id
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])