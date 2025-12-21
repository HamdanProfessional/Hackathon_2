"""Fix conversation and message UUID columns

Revision ID: e940f362bb65
Revises: 003
Create Date: 2025-12-21 13:55:28.865092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e940f362bb65'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop and recreate conversations table with UUID columns
    op.execute('DROP TABLE IF EXISTS messages CASCADE')
    op.execute('DROP TABLE IF EXISTS conversations CASCADE')

    op.create_table('conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False, server_default=sa.text("'New Conversation'")),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_conversations_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_conversations_created_at_desc', 'created_at')
    )

    op.create_table('messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tool_call_id', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name=op.f('fk_messages_conversation_id_conversations'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system', 'tool')", name='check_role_values'),
        sa.Index('idx_messages_conversation_created', 'conversation_id', 'created_at')
    )


def downgrade() -> None:
    # This migration is difficult to downgrade safely due to UUID to integer conversion
    # In production, you would need to handle data migration
    op.execute('DROP TABLE IF EXISTS messages CASCADE')
    op.execute('DROP TABLE IF EXISTS conversations CASCADE')
