# Database Migration Wizard - Evolution of TODO Edition

This guide documents the actual database migration patterns used in the Evolution of TODO project.

## Alembic Setup

### Initialize Alembic

```bash
cd backend

# Initialize Alembic
alembic init alembic

# This creates:
# alembic/
#   ├── versions/          # Migration files
#   ├── env.py             # Alembic environment
#   └── script.py.mako     # Migration template
# alembic.ini              # Configuration
```

### Configure alembic.ini

```ini
# alembic.ini
[alembiC]
# SQLAlchemy URL - use env variable for security
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost:5432/todo

# Location of migration files
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# Version path separator (for Alembic 1.10+)
version_path_separator = os

# Truncate slugs to 40 characters
truncate_slug_length = 40
```

## Creating Migrations

### Auto-Generate Migration

```bash
# Review changes and generate migration
alembic revision --autogenerate -m "Add user preferences table"

# This creates a new file in alembic/versions/
# Example: 20250101_120000_add_user_preferences_table.py
```

### Manual Migration

```bash
# Create empty migration
alembic revision -m "Add task indexes"

# Then edit the file manually
```

### Migration File Structure

```python
# alembic/versions/20250101_120000_add_user_preferences.py
"""Add user preferences table

Revision ID: abc123def456
Revises: 987zyx654321
Create Date: 2025-01-01 12:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = 'abc123def456'
down_revision: Union[str, None] = '987zyx654321'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_preferences table."""
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('show_completed', sa.Boolean(), nullable=True),
        sa.Column('compact_view', sa.Boolean(), nullable=True),
        sa.Column('dark_mode', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop user_preferences table."""
    op.drop_index(op.f('ix_user_preferences_user_id'), table_name='user_preferences')
    op.drop_table('user_preferences')
```

## Common Migration Patterns

### 1. Add New Table

```python
def upgrade() -> None:
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

def downgrade() -> None:
    op.drop_table('conversations')
```

### 2. Add Column to Existing Table

```python
def upgrade() -> None:
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'is_recurring')
```

### 3. Modify Column Type

```python
def upgrade() -> None:
    # Change enum to varchar (common workaround)
    op.execute("ALTER TABLE messages ALTER COLUMN role TYPE VARCHAR USING role::VARCHAR")

def downgrade() -> None:
    # Change back to enum
    op.execute("ALTER TABLE messages ALTER COLUMN role TYPE VARCHAR(20) USING role::VARCHAR(20)")
```

### 4. Add Index

```python
def upgrade() -> None:
    op.create_index('ix_tasks_user_id_created_at', 'tasks', ['user_id', sa.text('created_at DESC')])

def downgrade() -> None:
    op.drop_index('ix_tasks_user_id_created_at')
```

### 5. Data Migration

```python
def upgrade() -> None:
    # Add column first
    op.add_column('tasks', sa.Column('priority_id', sa.Integer(), nullable=True))

    # Migrate data
    from sqlalchemy.sql import table, column
    tasks = table('tasks', column('id'), column('priority'))

    connection = op.get_bind()
    connection.execute(
        tasks.update()
        .where(tasks.c.priority == 'high')
        .values(priority_id=3)
    )
    connection.execute(
        tasks.update()
        .where(tasks.c.priority == 'medium')
        .values(priority_id=2)
    )
    connection.execute(
        tasks.update()
        .where(tasks.c.priority == 'low')
        .values(priority_id=1)
    )

    # Make column non-nullable
    op.alter_column('tasks', 'priority_id', nullable=False)

def downgrade() -> None:
    # Revert changes
    op.drop_column('tasks', 'priority_id')
```

## Running Migrations

### Commands

```bash
# Check current version
alembic current

# View migration history
alembic history

# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123def456

# Downgrade one step
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade 987zyx654321

# Stamp current version (skip migrations)
alembic stamp head
```

### Handling Migration Conflicts

When multiple developers create migrations with the same down_revision:

```bash
# Merge migrations
alembic merge -m "Merge branch migrations" abc123 def456

# This creates a new migration with both parents
```

## Testing Migrations

```python
# tests/test_migrations.py
import pytest
from alembic import command
from alembic.config import Config


@pytest.fixture
def alembic_config():
    """Create Alembic config for testing."""
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", "sqlite+aiosqlite:///:memory:")
    return config


def test_upgrade_downgrade(alembic_config):
    """Test that upgrade and downgrade work."""
    # Upgrade to head
    command.upgrade(alembic_config, "head")

    # Downgrade to base
    command.downgrade(alembic_config, "base")

    # Upgrade again
    command.upgrade(alembic_config, "head")
```

## Production Migration Checklist

### Before Running
- [ ] Backup database
- [ ] Review migration SQL
- [ ] Test migration on staging
- [ ] Estimate downtime
- [ ] Prepare rollback plan

### During Migration
- [ ] Use `alembic upgrade head` with verbose flag
- [ ] Monitor for errors
- [ ] Check application logs

### After Migration
- [ ] Verify application works
- [ ] Check database integrity
- [ ] Monitor performance
- [ ] Update documentation

## Common Issues

### 1. Circular Dependencies

**Problem**: Table A references Table B, Table B references Table A

**Solution**: Create tables first, then add foreign keys
```python
def upgrade() -> None:
    # Create tables without FKs
    op.create_table('tasks', ...)
    op.create_table('subtasks', ...)

    # Add FKs after
    op.create_foreign_key('fk_subtasks_task', 'subtasks', 'tasks', ['task_id'], ['id'])
```

### 2. Large Table Migrations

**Problem**: Altering large tables takes too long

**Solution**: Use batching
```python
def upgrade() -> None:
    # Add column as nullable
    op.add_column('tasks', sa.Column('new_field', sa.String(), nullable=True))

    # Batch update data (run separately)
    # connection.execute("UPDATE tasks SET new_field = 'default' WHERE id > 0 AND id <= 10000")

    # Make non-nullable after data migration
    # op.alter_column('tasks', 'new_field', nullable=False)
```

### 3. Dropping Columns with Data

**Problem**: Accidentally drop column with important data

**Solution**: Always backup first
```bash
# Backup
pg_dump -U user -d todo > backup.sql

# Run migration
alembic upgrade head

# Verify before deleting backup
```

## Alembic Environment Configuration

```python
# alembic/env.py
from asyncio import run
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import your models
from app.models import SQLModel
from app.database import DATABASE_URL

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run async migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Migration Best Practices

1. **Always review auto-generated migrations** - They may not be perfect
2. **Write both upgrade and downgrade** - Enable rollbacks
3. **Use descriptive messages** - Explain what changed and why
4. **Test on local first** - Never test on production
5. **Keep migrations reversible** - Don't drop data unless necessary
6. **Use transactions** - Alembic wraps migrations in transactions
7. **Version control migrations** - Commit to git
8. **Communicate with team** - Coordinate simultaneous migrations
9. **Backup before production** - Always have a rollback plan
10. **Monitor after migration** - Watch for performance issues
