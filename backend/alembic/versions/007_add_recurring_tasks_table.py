"""Add recurring_tasks table for Phase V event-driven architecture

Revision ID: 007
Revises: 006
Create Date: 2025-12-26

This migration adds the recurring_tasks table to support automated task
creation based on recurrence patterns. The table includes:
- Recurrence pattern (daily, weekly, monthly, yearly)
- Start and end date configuration
- Next due date tracking for scheduler
- Priority assignment
- Active/inactive status

Feature: Recurring Tasks - Automated task creation on schedules
Phase: V - Event-Driven Architecture
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create recurring_tasks table with indexes and foreign keys."""

    # Create recurring_tasks table
    op.create_table(
        'recurring_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'user_id',
            postgresql.UUID(as_uuid=True),
            nullable=False
        ),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('recurrence_pattern', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('next_due_at', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('task_priority_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_priority_id'], ['priorities.id'], ondelete='SET NULL'),
    )

    # Create indexes for recurring_tasks table
    op.create_index('ix_recurring_tasks_id', 'recurring_tasks', ['id'])
    op.create_index('ix_recurring_tasks_user_id', 'recurring_tasks', ['user_id'])
    op.create_index('ix_recurring_tasks_next_due_at', 'recurring_tasks', ['next_due_at'])


def downgrade() -> None:
    """Drop recurring_tasks table and indexes."""

    # Drop indexes
    op.drop_index('ix_recurring_tasks_next_due_at', table_name='recurring_tasks')
    op.drop_index('ix_recurring_tasks_user_id', table_name='recurring_tasks')
    op.drop_index('ix_recurring_tasks_id', table_name='recurring_tasks')

    # Drop table
    op.drop_table('recurring_tasks')
