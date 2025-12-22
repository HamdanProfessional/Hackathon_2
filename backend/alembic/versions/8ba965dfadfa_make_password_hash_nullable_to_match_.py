"""Make password_hash nullable to match model definition

Revision ID: 8ba965dfadfa
Revises: 004
Create Date: 2025-12-22 20:16:08.320723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ba965dfadfa'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make password_hash column nullable to match the User model definition."""
    # Make password_hash nullable (it's a legacy field for compatibility)
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(length=255),
                    nullable=True)


def downgrade() -> None:
    """Revert password_hash to NOT NULL."""
    # Note: This might fail if there are NULL values in password_hash
    op.alter_column('users', 'password_hash',
                    existing_type=sa.String(length=255),
                    nullable=False)
