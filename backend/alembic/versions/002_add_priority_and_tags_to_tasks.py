"""add priority and tags to tasks

Revision ID: 002
Revises: 001
Create Date: 2025-12-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add priority and tags columns to tasks table."""
    # Add priority column with default value 'medium'
    op.add_column('tasks', sa.Column('priority',
        sa.Enum('low', 'medium', 'high', name='taskpriority'),
        nullable=False,
        server_default='medium'))

    # Add tags column with default empty string
    op.add_column('tasks', sa.Column('tags',
        sa.Text(),
        nullable=False,
        server_default=''))


def downgrade() -> None:
    """Remove priority and tags columns from tasks table."""
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
    # Drop the enum type (PostgreSQL specific)
    op.execute('DROP TYPE IF EXISTS taskpriority')
