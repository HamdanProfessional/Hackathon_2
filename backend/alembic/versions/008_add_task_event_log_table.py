"""Add task_event_log table for Phase V event audit trail

Revision ID: 008
Revises: 007
Create Date: 2025-12-26

This migration adds the task_event_log table to maintain an audit trail
of all task-related events. The table supports:
- Event type tracking (created, updated, completed, deleted, due_soon)
- Event data storage in JSONB format
- Timestamped event logging
- Cascade deletion when parent task is deleted

Feature: Event Logging - Audit trail for task lifecycle events
Phase: V - Event-Driven Architecture
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create task_event_log table with indexes and foreign keys."""

    # Create task_event_log table
    op.create_table(
        'task_event_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )

    # Create indexes for task_event_log table
    op.create_index('ix_task_event_log_id', 'task_event_log', ['id'])
    op.create_index('ix_task_event_log_task_id', 'task_event_log', ['task_id'])
    op.create_index('ix_task_event_log_event_type', 'task_event_log', ['event_type'])
    op.create_index('ix_task_event_log_created_at', 'task_event_log', ['created_at'])


def downgrade() -> None:
    """Drop task_event_log table and indexes."""

    # Drop indexes
    op.drop_index('ix_task_event_log_created_at', table_name='task_event_log')
    op.drop_index('ix_task_event_log_event_type', table_name='task_event_log')
    op.drop_index('ix_task_event_log_task_id', table_name='task_event_log')
    op.drop_index('ix_task_event_log_id', table_name='task_event_log')

    # Drop table
    op.drop_table('task_event_log')
