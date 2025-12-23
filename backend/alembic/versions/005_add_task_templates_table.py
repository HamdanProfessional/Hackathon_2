"""Add task_templates table for reusable task patterns

Revision ID: 005
Revises: 004
Create Date: 2025-12-23

This migration adds the task_templates table to allow users to save
and reuse common task patterns. Templates can include:
- Title and description
- Default priority
- Recurrence settings
- Tags (stored as JSON)
- Subtask templates (stored as JSON)

Feature: Task Templates - Save and reuse common task patterns
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create task_templates table with indexes and foreign keys."""

    # Create task_templates table
    op.create_table(
        'task_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'user_id',
            postgresql.UUID(as_uuid=True),
            nullable=False
        ),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority_id', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recurrence_pattern', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('subtasks_template', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['priority_id'], ['priorities.id'], ondelete='SET NULL'),
    )

    # Create indexes for task_templates table
    op.create_index('ix_task_templates_id', 'task_templates', ['id'])
    op.create_index('ix_task_templates_user_id', 'task_templates', ['user_id'])
    op.create_index('ix_task_templates_created_at', 'task_templates', ['created_at'])
    op.create_index('ix_task_templates_updated_at', 'task_templates', ['updated_at'])


def downgrade() -> None:
    """Drop task_templates table and indexes."""

    # Drop indexes
    op.drop_index('ix_task_templates_updated_at', table_name='task_templates')
    op.drop_index('ix_task_templates_created_at', table_name='task_templates')
    op.drop_index('ix_task_templates_user_id', table_name='task_templates')
    op.drop_index('ix_task_templates_id', table_name='task_templates')

    # Drop table
    op.drop_table('task_templates')
