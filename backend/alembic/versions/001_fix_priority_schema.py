"""Fix priority schema: create priorities table and migrate from enum

Revision ID: 001_fix_priority_schema
Revises: 8f1fe1b1db30
Create Date: 2025-12-22

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_fix_priority_schema'
down_revision: Union[str, None] = 'e940f362bb65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create priorities table and migrate from enum to foreign key."""

    # Check if priorities table exists, create if not
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    if 'priorities' not in inspector.get_table_names():
        # Create priorities table first
        op.create_table(
            'priorities',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.Column('level', sa.Integer(), nullable=False),
            sa.Column('color', sa.String(length=7), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

        # Create index for priorities table
        op.create_index('ix_priorities_id', 'priorities', ['id'], unique=True)

        # Insert default priority levels
        op.bulk_insert(
            sa.table(
                'priorities',
                sa.column('id', sa.Integer),
                sa.column('name', sa.String),
                sa.column('level', sa.Integer),
                sa.column('color', sa.String)
            ),
            [
                {'id': 1, 'name': 'low', 'level': 1, 'color': '#28a745'},
                {'id': 2, 'name': 'medium', 'level': 2, 'color': '#ffc107'},
                {'id': 3, 'name': 'high', 'level': 3, 'color': '#dc3545'}
            ]
        )

    # Check if tasks table has priority_id column
    tasks_columns = [col['name'] for col in inspector.get_columns('tasks')]

    if 'priority_id' not in tasks_columns:
        # Add priority_id column to tasks table (nullable initially)
        op.add_column('tasks', sa.Column('priority_id', sa.Integer(), nullable=True))

        # Create foreign key constraint
        op.create_foreign_key(
            'fk_tasks_priority_id_priorities',
            'tasks', 'priorities',
            ['priority_id'], ['id'],
            ondelete='SET NULL'
        )

        # Check if old priority enum column exists and migrate data
        if 'priority' in tasks_columns:
            # Migrate data from priority enum to priority_id
            # Enum values: 'LOW' -> 1, 'MEDIUM' -> 2, 'HIGH' -> 3
            op.execute("""
                UPDATE tasks
                SET priority_id = CASE priority
                    WHEN 'LOW' THEN 1
                    WHEN 'MEDIUM' THEN 2
                    WHEN 'HIGH' THEN 3
                    ELSE 2  -- Default to medium for any unexpected values
                END
            """)

            # Drop the old priority enum column
            op.drop_column('tasks', 'priority')

        # Make priority_id NOT NULL after migration
        op.alter_column('tasks', 'priority_id', nullable=False)

        # Create index for priority_id if it doesn't exist
        indexes = inspector.get_indexes('tasks')
        if not any(idx['name'] == 'ix_tasks_priority_id' for idx in indexes):
            op.create_index('ix_tasks_priority_id', 'tasks', ['priority_id'])


def downgrade() -> None:
    """Revert back to enum-based priority system."""

    # Add back the priority enum column
    priority_enum = sa.Enum('LOW', 'MEDIUM', 'HIGH', name='taskpriority')
    op.add_column('tasks', sa.Column('priority', priority_enum, nullable=False))

    # Migrate data back from priority_id to enum
    op.execute("""
        UPDATE tasks
        SET priority = CASE priority_id
            WHEN 1 THEN 'LOW'
            WHEN 2 THEN 'MEDIUM'
            WHEN 3 THEN 'HIGH'
            ELSE 'MEDIUM'  -- Default to medium
        END
    """)

    # Drop foreign key constraint and priority_id column
    op.drop_constraint('fk_tasks_priority_id_priorities', 'tasks', type_='foreignkey')
    op.drop_index('ix_tasks_priority_id', table_name='tasks')
    op.drop_column('tasks', 'priority_id')

    # Drop priorities table
    op.drop_index('ix_priorities_id', table_name='priorities')
    op.drop_table('priorities')

    # Drop the enum type
    priority_enum.drop(op.get_bind())