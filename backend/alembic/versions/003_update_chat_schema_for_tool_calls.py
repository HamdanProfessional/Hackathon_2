"""Update chat schema for tool_calls support and UUID primary keys

Revision ID: 003
Revises: 69ef5db393b3
Create Date: 2025-12-20

This migration updates the conversations and messages tables for Phase III AI Chatbot:

CONVERSATION CHANGES:
- Change id from Integer to UUID
- Add title field (String(200), default="New Conversation")
- Add index on created_at DESC

MESSAGE CHANGES:
- Change id from Integer to UUID
- Change conversation_id from Integer FK to UUID FK
- Add tool_calls JSON field (nullable) - stores OpenAI tool_calls format
- Add tool_call_id String(100, nullable)
- Add name String(100, nullable)
- Update role constraint to include 'system' and 'tool'
- Add composite index (conversation_id, created_at ASC)

MIGRATION STRATEGY:
Since we're changing primary key types, we'll:
1. Drop existing conversations and messages tables (assuming no production data)
2. Recreate with new UUID-based schema
3. Re-add all indexes and constraints

NOTE: This is a destructive migration. If production data exists, backup first!
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '69ef5db393b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade to UUID-based schema with tool_calls support.

    WARNING: This migration drops and recreates tables!
    Backup any existing conversations/messages before running.
    """

    # Step 1: Drop existing trigger and function
    op.execute("DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;")
    op.execute("DROP FUNCTION IF EXISTS update_conversation_timestamp();")

    # Step 2: Drop existing tables (in order due to foreign keys)
    op.drop_table('messages')
    op.drop_table('conversations')

    # Step 3: Recreate conversations table with UUID primary key
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False, server_default='New Conversation'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Step 4: Create indexes for conversations table
    op.create_index('ix_conversations_id', 'conversations', ['id'])
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_updated_at', 'conversations', ['updated_at'])
    op.create_index('idx_conversations_created_at_desc', 'conversations', ['created_at'],
                    postgresql_ops={'created_at': 'DESC'})

    # Step 5: Recreate messages table with UUID primary key and new fields
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tool_call_id', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system', 'tool')", name='check_role_values'),
    )

    # Step 6: Create indexes for messages table
    op.create_index('ix_messages_id', 'messages', ['id'])
    op.create_index('ix_messages_role', 'messages', ['role'])
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

    # Step 7: Recreate trigger function to update conversation.updated_at when message inserted
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

    # Step 8: Recreate trigger on messages table
    op.execute("""
        CREATE TRIGGER trigger_update_conversation_timestamp
        AFTER INSERT ON messages
        FOR EACH ROW
        EXECUTE FUNCTION update_conversation_timestamp();
    """)


def downgrade() -> None:
    """Downgrade to Integer-based schema without tool_calls support.

    WARNING: This migration drops and recreates tables!
    All conversation data will be lost.
    """

    # Step 1: Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;")
    op.execute("DROP FUNCTION IF EXISTS update_conversation_timestamp();")

    # Step 2: Drop tables (in order due to foreign keys)
    op.drop_table('messages')
    op.drop_table('conversations')

    # Step 3: Recreate conversations table with Integer primary key (original schema)
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Step 4: Create indexes for conversations table
    op.create_index('ix_conversations_id', 'conversations', ['id'])
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_updated_at', 'conversations', ['updated_at'])

    # Step 5: Recreate messages table with Integer primary key (original schema)
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

    # Step 6: Create indexes for messages table
    op.create_index('ix_messages_id', 'messages', ['id'])
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

    # Step 7: Recreate trigger function
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

    # Step 8: Recreate trigger
    op.execute("""
        CREATE TRIGGER trigger_update_conversation_timestamp
        AFTER INSERT ON messages
        FOR EACH ROW
        EXECUTE FUNCTION update_conversation_timestamp();
    """)
