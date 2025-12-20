"""merge migrations

Revision ID: 4257a174db1b
Revises: 002, 8f1fe1b1db30
Create Date: 2025-12-19 21:43:05.392321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4257a174db1b'
down_revision: Union[str, None] = ('002', '8f1fe1b1db30')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
