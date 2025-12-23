"""Add subtasks table for breaking tasks into smaller steps

Revision ID: 006
Revises: 005
Create Date: 2025-12-23

This migration adds the subtasks table to allow users to break down
their tasks into smaller, manageable steps. Subtasks include:
- Title and optional description
- Completion status tracking
- Sort order for custom ordering
- Cascade deletion when parent task is deleted

Feature: Subtasks - Break tasks into smaller steps
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create subtasks table with indexes and foreign keys."""

    # Create subtasks table
    op.create_table(
        'subtasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )

    # Create indexes for subtasks table
    op.create_index('ix_subtasks_id', 'subtasks', ['id'])
    op.create_index('ix_subtasks_task_id', 'subtasks', ['task_id'])
    op.create_index('ix_subtasks_sort_order', 'subtasks', ['sort_order'])
    op.create_index('ix_subtasks_created_at', 'subtasks', ['created_at'])


def downgrade() -> None:
    """Drop subtasks table and indexes."""

    # Drop indexes
    op.drop_index('ix_subtasks_created_at', table_name='subtasks')
    op.drop_index('ix_subtasks_sort_order', table_name='subtasks')
    op.drop_index('ix_subtasks_task_id', table_name='subtasks')
    op.drop_index('ix_subtasks_id', table_name='subtasks')

    # Drop table
    op.drop_table('subtasks')
