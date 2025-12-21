# Phase I to Phase II Migration Guide

## Overview
Guide for migrating in-memory task management to SQLModel database in Phase II.

## Migration Steps

### 1. Replace Task Model

**Phase I (dataclass):**
```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

**Phase II (SQLModel):**
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    # Add user relationship for multi-user support
    user_id: str = Field(foreign_key="users.id")
```

### 2. Update TaskManager

**Phase I (In-memory):**
```python
class TaskManager:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def create_task(self, title: str, description: str = None) -> Task:
        # In-memory creation
```

**Phase II (Database):**
```python
from sqlmodel import Session, select

class TaskManager:
    def __init__(self, session: Session):
        self.session = session

    def create_task(self, user_id: str, title: str, description: str = None) -> Task:
        task = Task(user_id=user_id, title=title, description=description)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
```

### 3. Add Database Configuration

```python
# config.py
from sqlalchemy import create_engine
from sqlmodel import Session

DATABASE_URL = "postgresql://user:pass@host/db"

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
```

### 4. Create Migration Script

```python
# migrate_phase1_to_phase2.py
"""Export Phase I tasks for Phase II import."""

def export_tasks_to_json(task_manager: TaskManager, filename: str):
    """Export all tasks to JSON file."""
    import json

    tasks_data = []
    for task in task_manager.list_tasks():
        tasks_data.append({
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'created_at': task.created_at.isoformat()
        })

    with open(filename, 'w') as f:
        json.dump(tasks_data, f, indent=2)
```

## Key Changes

### Database Dependencies
```python
# requirements.txt
sqlmodel
psycopg2-binary  # For PostgreSQL
alembic         # For migrations
```

### Session Management
- All operations now require database session
- Session must be committed to save changes
- Use context managers for session handling

### User Isolation
- Add `user_id` field to Task model
- Filter all queries by user
- Update all methods to accept `user_id` parameter

### Error Handling Changes
- SQLAlchemy errors for database issues
- Constraint violations for invalid data
- Connection errors for database problems

## Updated Method Signatures

### Create Task
```python
# Phase I
create_task(title: str, description: str = None) -> Task

# Phase II
create_task(user_id: str, title: str, description: str = None) -> Task
```

### List Tasks
```python
# Phase I
list_tasks(filter_status: str = None) -> List[Task]

# Phase II
list_tasks(user_id: str, filter_status: str = None) -> List[Task]
```

### Get Task
```python
# Phase I
get_task(task_id: int) -> Task

# Phase II
get_task(user_id: str, task_id: int) -> Task
```

## Testing Migration

### 1. Unit Tests
```python
def test_task_crud_with_database():
    """Test CRUD operations with SQLModel."""
    with Session(engine) as session:
        tm = TaskManager(session)

        # Create
        task = tm.create_task("user1", "Test task")
        assert task.id is not None

        # Read
        retrieved = tm.get_task("user1", task.id)
        assert retrieved.title == "Test task"

        # Update
        tm.update_task("user1", task.id, title="Updated")

        # Delete
        deleted = tm.delete_task("user1", task.id)
        assert deleted.title == "Updated"
```

### 2. Data Migration Test
```python
def test_data_migration():
    """Test exporting Phase I data to Phase II format."""
    # Create Phase I tasks
    old_tm = PhaseOneTaskManager()
    old_tm.create_task("Task 1", "Description 1")

    # Export
    export_tasks_to_json(old_tm, "migration_data.json")

    # Verify JSON format
    with open("migration_data.json") as f:
        data = json.load(f)

    assert len(data) == 1
    assert data[0]['title'] == "Task 1"
```

## Benefits of Migration

1. **Persistence**: Tasks survive application restarts
2. **Multi-user**: Support for multiple users
3. **Scalability**: Handle millions of tasks
4. **Query Power**: Advanced filtering and sorting
5. **Transactions**: ACID compliance
6. **Backup**: Easy database backups