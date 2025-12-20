"""Fix conversations table user_id to be UUID type

Revision ID: 0c94a30879c6
Revises: 4257a174db1b
Create Date: 2025-12-19 21:51:08.594368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0c94a30879c6'
down_revision: Union[str, None] = '4257a174db1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop and recreate conversations and messages tables with correct UUID type."""

    # Since we're in development/hackathon mode, it's safer to drop and recreate
    # the tables rather than attempting complex data migration

    # Drop existing tables (cascade handles foreign key dependencies)
    op.execute('DROP TABLE IF EXISTS messages CASCADE')
    op.execute('DROP TABLE IF EXISTS conversations CASCADE')

    # Recreate conversations table with correct UUID type for user_id
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for conversations table
    op.create_index('ix_conversations_id', 'conversations', ['id'])
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_updated_at', 'conversations', ['updated_at'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_role_values'),
    )

    # Create indexes for messages table
    op.create_index('ix_messages_id', 'messages', ['id'])
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

    # Create trigger for automatically updating updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    op.execute("""
        CREATE TRIGGER update_conversations_updated_at
            BEFORE UPDATE ON conversations
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    """Drop the correctly typed tables (no downgrade path for development)."""

    # Drop the trigger
    op.execute('DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')

    # Drop tables
    op.execute('DROP TABLE IF EXISTS messages CASCADE')
    op.execute('DROP TABLE IF EXISTS conversations CASCADE')

    # Note: We don't recreate the old incorrect schema in downgrade
    # This is acceptable for hackathon/development environment