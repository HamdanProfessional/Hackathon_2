---
name: db-migration-wizard
description: Generate Alembic migrations with alembic revision --autogenerate -m 'description', handle schema changes by adding nullable columns first (op.add_column() then op.alter_column(nullable=False)), rename fields with op.alter_column(new_column_name='name'), convert types with op.execute() data migration then op.alter_column(type_=sa.Integer()), and apply via alembic upgrade head to PostgreSQL. Use when SQLModel definitions in backend/app/models/ change, adding foreign keys, or fixing column type mismatches.
---

# Database Migration Wizard Skill

Generate Alembic migrations, handle schema changes, and apply database updates safely.

## File Locations

```
backend/
├── alembic/
│   ├── versions/
│   │   └── 001_add_tasks_table.py    # Migration files
│   └── env.py                         # Alembic configuration
├── app/
│   └── models/
│       └── task.py                     # SQLModel definitions
└── alembic.ini                         # Alembic settings
```

## Quick Commands

```bash
# Generate migration
cd backend
alembic revision --autogenerate -m "Description of changes"

# Apply migration locally
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Apply migration in production pod
kubectl exec <backend-pod> -- alembic upgrade head
```

## Common Scenarios

### Scenario 1: Add New Column to Existing Table
**User Request**: "Add a due_date column to the tasks table"

**Commands**:
```bash
# 1. Update model
# File: backend/app/models/task.py
# Add: due_date: Optional[datetime] = Field(default=None)

# 2. Generate migration
cd backend
alembic revision --autogenerate -m "Add due_date to tasks"

# 3. Review migration
# File: alembic/versions/xxx_add_due_date.py
# Verify it contains: op.add_column('tasks', sa.Column('due_date', sa.DateTime()))

# 4. Apply locally
alembic upgrade head

# 5. Test
curl -X POST http://localhost:8000/tasks -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Test", "due_date": "2025-12-31T00:00:00Z"}'

# 6. Apply to production
kubectl exec deployment/backend -- alembic upgrade head
```

### Scenario 2: Fix Column Type Mismatch
**Error**: `Backend shows "column priority_id does not exist" or type error`

**Commands**:
```bash
# 1. Check database
kubectl exec <backend-pod> -- python -c "
from app.database import engine
from sqlmodel import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT * FROM tasks LIMIT 1'))
    print(result.keys())
"

# 2. If shows 'priority' (string) instead of 'priority_id' (int):
# Generate migration to rename and convert
alembic revision -m "Rename priority to priority_id"

# 3. Edit migration manually:
def upgrade():
    # Clear incompatible data
    op.execute("UPDATE tasks SET priority = NULL")
    # Rename column
    op.alter_column('tasks', 'priority', new_column_name='priority_id')
    # Change type
    op.alter_column('tasks', 'priority_id', type_=sa.Integer())

# 4. Apply
alembic upgrade head
```

### Scenario 3: Rename Column While Preserving Data
**User Request**: "Rename priority column to priority_level"

**Actions**:
1. **Update SQLModel** - Change field name in model
2. **Create migration manually** (autogenerate won't detect rename):
```python
def upgrade():
    op.alter_column('tasks', 'priority', new_column_name='priority_level')

def downgrade():
    op.alter_column('tasks', 'priority_level', new_column_name='priority')
```
3. **Do NOT use drop + add** - That would lose data

### Scenario 4: Add Foreign Key Constraint
**User Request**: "Add user_id foreign key to tasks table"

**Actions**:
1. **Check users table exists**:
```sql
SELECT COUNT(*) FROM users;
```
2. **Update SQLModel** with foreign key:
```python
from uuid import UUID

class Task(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="users.id", index=True)
```
3. **Generate migration** - Should create FK constraint
4. **Verify constraint created**:
```sql
SELECT * FROM information_schema.table_constraints
WHERE table_name = 'tasks';
```

### Scenario 5: Add Not Null Constraint to Existing Column
**User Request**: "Make title field required"

**Actions**:
1. **First ensure no NULL values exist**:
```python
def upgrade():
    op.execute("UPDATE tasks SET title = 'Untitled' WHERE title IS NULL")
    op.alter_column('tasks', 'title', nullable=False)
```
2. **Update SQLModel** to remove Optional:
```python
# Before: title: Optional[str]
# After: title: str
```
3. **Test rollback**: `alembic downgrade -1` then `alembic upgrade +1`

---

## Quick Templates

### Migration File Template
```python
"""Add column_name to table_name

Revision ID: xxx
Revises: yyy
Create Date: 2025-01-02
"""
from alembic import op
import sqlalchemy as sa

revision = 'xxx'
down_revision = 'yyy'

def upgrade():
    op.add_column('table_name', sa.Column('column_name', sa.Type(), nullable=True))

def downgrade():
    op.drop_column('table_name', 'column_name')
```

### Common Migration Patterns
```python
# Add nullable column
op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))

# Add index
op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])

# Add foreign key
op.create_foreign_key('fk_tasks_user', 'tasks', 'users', ['user_id'], ['id'])

# Rename column
op.alter_column('tasks', 'old_name', new_column_name='new_name')

# Change type (with data clearing first)
op.execute("UPDATE tasks SET col = NULL")
op.alter_column('tasks', 'col', type_=sa.Integer())
```

### Safety Checklist Before Applying
- [ ] Backed up production database (Neon auto-backups enabled)
- [ ] Reviewed generated SQL in migration file
- [ ] Tested migration on local SQLite/Postgres
- [ ] Verified rollback (`downgrade()`) works
- [ ] Checked for data loss scenarios
- [ ] Updated SQLModel models match new schema
- [ ] Updated Pydantic schemas in backend/app/schemas/
- [ ] Updated TypeScript types in frontend
- [ ] Documented breaking changes

---
cd backend
alembic revision --autogenerate -m "Add is_recurring column to tasks"
```

**Migration File** (`alembic/versions/xxxx_add_is_recurring.py`):
```python
"""Add is_recurring column to tasks

Revision ID: xxxx
Revises: yyyy
Create Date: 2025-12-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'xxxx'
down_revision = 'yyyy'
branch_labels = None
depends_on = None


def upgrade():
    # Add column as nullable
    op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=True))

    # Set default value for existing rows
    op.execute("UPDATE tasks SET is_recurring = FALSE WHERE is_recurring IS NULL")

    # Make non-nullable after setting defaults
    op.alter_column('tasks', 'is_recurring', nullable=False)


def downgrade():
    op.drop_column('tasks', 'is_recurring')
```

**Apply Migration**:
```bash
# Local testing
alembic upgrade head

# Production (via kubectl)
kubectl exec <backend-pod> -c backend -- alembic upgrade head
```

### 2. Renaming Column (Preserve Data)

**Problem**: Backend expects `priority_id` but database has `priority`

**SQLModel Update**:
```python
# backend/app/models/task.py
class Task(SQLModel, table=True):
    # OLD: priority: str
    # NEW: priority_id: Optional[int]

    priority_id: Optional[int] = Field(
        default=None,
        nullable=True,
        foreign_key="priorities.id",
        description="Task priority level (1=High, 2=Normal, 3=Low)"
    )
```

**Migration File**:
```python
def upgrade():
    # Rename column (preserves data)
    op.alter_column('tasks', 'priority', new_column_name='priority_id')


def downgrade():
    op.alter_column('tasks', 'priority_id', new_column_name='priority')
```

**Direct SQL** (when migration not feasible):
```python
# Via kubectl exec
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE tasks RENAME COLUMN priority TO priority_id'))
    conn.commit()
"
```

### 3. Converting Data Type (String → Integer)

**Problem**: Column has string data ('high', 'normal', 'low') but needs integers (1, 2, 3)

**Migration Strategy**:
```python
def upgrade():
    # Step 1: Clear incompatible data
    op.execute("UPDATE tasks SET priority_id = NULL")

    # Step 2: Change column type
    op.alter_column('tasks', 'priority_id',
                    type_=sa.Integer(),
                    existing_type=sa.String(),
                    nullable=True)


def downgrade():
    op.alter_column('tasks', 'priority_id',
                    type_=sa.String(),
                    existing_type=sa.Integer())
```

**With Data Conversion**:
```python
def upgrade():
    # Map string values to integers
    op.execute("""
        UPDATE tasks
        SET priority_id = CASE priority_id
            WHEN 'high' THEN 1
            WHEN 'normal' THEN 2
            WHEN 'low' THEN 3
            ELSE NULL
        END
    """)

    # Change column type
    op.alter_column('tasks', 'priority_id',
                    type_=sa.Integer(),
                    existing_type=sa.String())
```

### 4. Making Column Nullable/Non-Nullable

**Add NOT NULL Constraint**:
```python
def upgrade():
    # First, ensure no NULL values exist
    op.execute("UPDATE tasks SET completed = FALSE WHERE completed IS NULL")

    # Then add NOT NULL constraint
    op.alter_column('tasks', 'completed', nullable=False)


def downgrade():
    op.alter_column('tasks', 'completed', nullable=True)
```

**Remove NOT NULL Constraint**:
```python
def upgrade():
    # Allow NULL values
    op.alter_column('tasks', 'priority_id', nullable=True)


def downgrade():
    op.alter_column('tasks', 'priority_id', nullable=False)
```

### 5. Adding Foreign Key Constraint

**Create Reference Table First**:
```python
# Migration 1: Create priorities table
def upgrade():
    op.create_table('priorities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(20), nullable=False),
        sa.Column('color', sa.String(7), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default values
    op.execute("""
        INSERT INTO priorities (id, name, color) VALUES
        (1, 'High', '#ef4444'),
        (2, 'Normal', '#3b82f6'),
        (3, 'Low', '#10b981')
    """)


# Migration 2: Add FK constraint
def upgrade():
    op.create_foreign_key(
        'fk_tasks_priority_id',
        'tasks', 'priorities',
        ['priority_id'], ['id'],
        ondelete='SET NULL'
    )
```

### 6. Adding Index for Performance

**Migration File**:
```python
def upgrade():
    # Add index for faster queries
    op.create_index(
        'ix_tasks_user_id_completed',
        'tasks',
        ['user_id', 'completed']
    )


def downgrade():
    op.drop_index('ix_tasks_user_id_completed', table_name='tasks')
```

## Direct Database Access (Emergency)

### Via Kubernetes Pod

```bash
# Execute SQL directly
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    # Your SQL here
    result = conn.execute(text('SELECT * FROM tasks LIMIT 5'))
    for row in result:
        print(row)
"
```

### Common Emergency Fixes

**Add missing column**:
```python
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE NOT NULL'))
    conn.commit()
"
```

**Rename column**:
```python
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE tasks RENAME COLUMN priority TO priority_id'))
    conn.commit()
"
```

**Clear data before type change**:
```python
kubectl exec <backend-pod> -c backend -- python -c "
from sqlmodel import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    conn.execute(text('UPDATE tasks SET priority_id = NULL'))
    conn.execute(text('ALTER TABLE tasks ALTER COLUMN priority_id DROP NOT NULL'))
    conn.execute(text('ALTER TABLE tasks ALTER COLUMN priority_id TYPE INTEGER USING NULL'))
    conn.commit()
"
```

## Migration Checklist

Before applying migrations:
- [ ] Backup production database (Neon has automatic backups)
- [ ] Test migration on local SQLite
- [ ] Review generated SQL in migration file
- [ ] Check for data loss scenarios
- [ ] Test rollback procedure (downgrade)
- [ ] Update SQLModel models to match new schema
- [ ] Update Pydantic schemas in `backend/app/schemas/`
- [ ] Verify API endpoints still work
- [ ] Check frontend compatibility (TypeScript types)
- [ ] Document breaking changes in commit message

After applying migrations:
- [ ] Verify data integrity (check row counts, values)
- [ ] Test all CRUD operations via API
- [ ] Check for database locks or performance issues
- [ ] Monitor error logs for 500 errors
- [ ] Update API documentation if schema changed

## Common Pitfalls

1. **NOT NULL Constraints**: Always add nullable first, set defaults, then make non-nullable
   ```python
   # ❌ WRONG - Will fail if existing rows have NULL
   op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=False))

   # ✅ CORRECT - Three-step process
   op.add_column('tasks', sa.Column('is_recurring', sa.Boolean(), nullable=True))
   op.execute("UPDATE tasks SET is_recurring = FALSE WHERE is_recurring IS NULL")
   op.alter_column('tasks', 'is_recurring', nullable=False)
   ```

2. **Column Renames**: Use `alter_column()`, not drop + add (preserves data)
   ```python
   # ❌ WRONG - Loses data
   op.drop_column('tasks', 'priority')
   op.add_column('tasks', sa.Column('priority_id', sa.Integer()))

   # ✅ CORRECT - Preserves data
   op.alter_column('tasks', 'priority', new_column_name='priority_id')
   ```

3. **Type Changes**: May require data conversion or clearing
   ```python
   # ❌ WRONG - Fails if data incompatible
   op.alter_column('tasks', 'priority_id', type_=sa.Integer())

   # ✅ CORRECT - Clear or convert first
   op.execute("UPDATE tasks SET priority_id = NULL")
   op.alter_column('tasks', 'priority_id', type_=sa.Integer(), postgresql_using='priority_id::integer')
   ```

4. **Foreign Keys**: Create referenced table before adding FK constraint

5. **Indexes**: Add indexes AFTER data migration for better performance

6. **SQLite Limitations**: Limited ALTER TABLE support (may need table recreation)

## Example Usage

**Scenario**: Backend returns "column tasks.priority_id does not exist"

**Steps**:
1. Check database: Column is named `priority` (string)
2. Check model: Expects `priority_id` (integer FK)
3. Update SQLModel to use `priority_id: Optional[int]`
4. Generate migration: `alembic revision --autogenerate -m "Rename priority to priority_id"`
5. Review migration: Ensure it uses `alter_column` rename
6. Clear data: `UPDATE tasks SET priority = NULL` (if type incompatible)
7. Apply migration: `alembic upgrade head`
8. Update frontend TypeScript types to use `priority_id: number | null`
9. Test API: Create task, verify priority_id works

## Quality Checklist
Before finalizing:
- [ ] Migration file has both `upgrade()` and `downgrade()`
- [ ] Data preservation strategy in place
- [ ] NULL handling for new columns
- [ ] Type conversions handle existing data
- [ ] Foreign key constraints reference existing tables
- [ ] Indexes added for query optimization
- [ ] Migration tested locally before production
- [ ] Rollback plan documented
- [ ] API and frontend updated to match schema
- [ ] No hardcoded values (use environment variables)
