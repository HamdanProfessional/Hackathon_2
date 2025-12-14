"""Add conversations and messages tables for Phase III AI Chatbot

Revision ID: 001
Revises:
Create Date: 2025-12-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create conversations and messages tables with indexes and triggers."""

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
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
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

    # Create trigger function to update conversation.updated_at when message inserted
    op.execute("""
        CREATE OR REPLACE FUNCTION update_conversation_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            UPDATE conversations
            SET updated_at = NEW.created_at
            WHERE id = NEW.conversation_id;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on messages table
    op.execute("""
        CREATE TRIGGER trigger_update_conversation_timestamp
        AFTER INSERT ON messages
        FOR EACH ROW
        EXECUTE FUNCTION update_conversation_timestamp();
    """)


def downgrade() -> None:
    """Drop conversations and messages tables, indexes, and triggers."""

    # Drop trigger first
    op.execute("DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;")
    op.execute("DROP FUNCTION IF EXISTS update_conversation_timestamp();")

    # Drop messages table (indexes dropped automatically)
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_index('ix_messages_id', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table (indexes dropped automatically)
    op.drop_index('ix_conversations_updated_at', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_index('ix_conversations_id', table_name='conversations')
    op.drop_table('conversations')
