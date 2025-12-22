"""Add missing tool_call_id and name columns to messages table

Revision ID: 5e990c3ddfe4
Revises: 001_fix_priority_schema
Create Date: 2025-12-22 18:29:31.679333

This migration adds the tool_call_id and name columns to the messages table
if they don't already exist. These columns are required for OpenAI tool calls support.

SAFETY: This migration uses conditional logic to only add columns if they don't exist.
It's safe to run on databases that already have these columns (idempotent).

Columns added:
- tool_call_id: String(100), nullable=True - Links tool role messages to assistant's tool_calls[].id
- name: String(100), nullable=True - Function name for tool role messages
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '5e990c3ddfe4'
down_revision: Union[str, None] = '001_fix_priority_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    """Add tool_call_id and name columns to messages table if they don't exist."""

    # Add tool_call_id column if it doesn't exist
    if not column_exists('messages', 'tool_call_id'):
        op.add_column('messages', sa.Column('tool_call_id', sa.String(length=100), nullable=True))
        print("Added column 'tool_call_id' to messages table")
    else:
        print("Column 'tool_call_id' already exists in messages table - skipping")

    # Add name column if it doesn't exist
    if not column_exists('messages', 'name'):
        op.add_column('messages', sa.Column('name', sa.String(length=100), nullable=True))
        print("Added column 'name' to messages table")
    else:
        print("Column 'name' already exists in messages table - skipping")


def downgrade() -> None:
    """Remove tool_call_id and name columns from messages table if they exist."""

    # Drop name column if it exists
    if column_exists('messages', 'name'):
        op.drop_column('messages', 'name')
        print("Dropped column 'name' from messages table")
    else:
        print("Column 'name' does not exist in messages table - skipping")

    # Drop tool_call_id column if it exists
    if column_exists('messages', 'tool_call_id'):
        op.drop_column('messages', 'tool_call_id')
        print("Dropped column 'tool_call_id' from messages table")
    else:
        print("Column 'tool_call_id' does not exist in messages table - skipping")
