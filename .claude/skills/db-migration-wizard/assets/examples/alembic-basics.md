# Alembic Migration Example

## Create Migration

```bash
# Generate a new migration
alembic revision --autogenerate -m "add_user_table"

# Output: versions/001_add_user_table.py
```

## Migration File

```python
"""add user table

Revision ID: 001
Revises:
Create Date: 2025-01-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade():
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
```

## Apply Migration

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade 001

# Downgrade one revision
alembic downgrade -1

# Show current version
alembic current

# Show history
alembic history
```
