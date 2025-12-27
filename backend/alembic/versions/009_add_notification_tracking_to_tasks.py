"""Add notification tracking and recurring task link to tasks table for Phase V

Revision ID: 009
Revises: 008
Create Date: 2025-12-26

This migration adds two new columns to the tasks table:
1. notified - Track if due date notification has been sent
2. recurring_task_id - Link to parent recurring_tasks entry

These columns support:
- Notification system to prevent duplicate alerts
- Relationship between generated tasks and their recurring task template
- Cascade behavior: recurring task deletion SETS NULL on tasks

Feature: Recurring Tasks - Task generation and notification tracking
Phase: V - Event-Driven Architecture
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add notification tracking and recurring task foreign key to tasks table."""

    # Add notified column (default False - no notification sent yet)
    op.add_column(
        'tasks',
        sa.Column('notified', sa.Boolean(), nullable=False, server_default='false')
    )

    # Add recurring_task_id column (nullable - only set for recurring tasks)
    op.add_column(
        'tasks',
        sa.Column('recurring_task_id', sa.Integer(), nullable=True)
    )

    # Create foreign key to recurring_tasks table
    op.create_foreign_key(
        'fk_tasks_recurring_task_id',
        'tasks', 'recurring_tasks',
        ['recurring_task_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create index on recurring_task_id for queries
    op.create_index('ix_tasks_recurring_task_id', 'tasks', ['recurring_task_id'])


def downgrade() -> None:
    """Remove notification tracking and recurring task foreign key from tasks table."""

    # Drop index
    op.drop_index('ix_tasks_recurring_task_id', table_name='tasks')

    # Drop foreign key
    op.drop_constraint('fk_tasks_recurring_task_id', 'tasks', type_='foreignkey')

    # Drop columns
    op.drop_column('tasks', 'recurring_task_id')
    op.drop_column('tasks', 'notified')
