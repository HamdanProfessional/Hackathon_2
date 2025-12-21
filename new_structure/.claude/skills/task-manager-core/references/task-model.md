# Task Model Reference

## Task Dataclass

The `Task` dataclass is the core data model for todo items:

```python
@dataclass
class Task:
    id: int                    # Unique identifier (auto-assigned)
    title: str                 # Task title (required, 1-200 chars)
    description: str           # Optional description (max 1000 chars)
    completed: bool = False    # Completion status (default: False)
    created_at: datetime       # Creation timestamp (auto-generated)
```

## Field Details

### id: int
- **Purpose**: Unique identifier for each task
- **Generation**: Auto-increment starting from 1
- **Immutable**: Cannot be changed after creation
- **Usage**: Reference task in all operations

### title: str
- **Purpose**: Brief task description
- **Required**: Must be provided and non-empty
- **Length**: 1-200 characters
- **Validation**: Stripped of leading/trailing whitespace
- **Display**: Primary identifier in UI

### description: str
- **Purpose**: Detailed task information
- **Optional**: Defaults to empty string
- **Length**: Maximum 1000 characters
- **Usage**: Additional context, notes, or details
- **Formatting**: Plain text, no markup

### completed: bool
- **Purpose**: Track completion status
- **Default**: False (task starts incomplete)
- **Operation**: Toggled with `toggle_complete()`
- **Display**: Shows as ✓ (complete) or ✗ (incomplete)

### created_at: datetime
- **Purpose**: Track when task was created
- **Generation**: Auto-set to current UTC time
- **Format**: ISO 8601 datetime
- **Usage**: Sorting, time tracking, debugging

## Validation Rules

### Title Validation
```python
def validate_title(title: str) -> str:
    """Validate and clean task title."""
    if not title or not title.strip():
        raise ValueError("Task title cannot be empty")
    if len(title) > 200:
        raise ValueError("Task title cannot exceed 200 characters")
    return title.strip()
```

### Description Validation
```python
def validate_description(description: str) -> str:
    """Validate and clean task description."""
    if description:
        description = description.strip()
        if len(description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
    return description or ""
```

## Usage Examples

### Creating a Task
```python
# Basic task
task = Task(
    id=1,
    title="Buy groceries"
)

# Task with description
task = Task(
    id=2,
    title="Call mom",
    description="Remember to ask about the family reunion"
)

# Completed task
task = Task(
    id=3,
    title="Finish project",
    completed=True,
    created_at=datetime.now()
)
```

### Checking Status
```python
# Check if task is complete
if task.completed:
    print(f"✓ {task.title}")
else:
    print(f"✗ {task.title}")

# Format created date
print(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
```

### Display Task
```python
def format_task(task: Task) -> str:
    """Format task for display."""
    status = "✓" if task.completed else "✗"
    desc = f" - {task.description}" if task.description else ""
    return f"{task.id}: {task.title} {status}{desc}"
```

## Migration Notes

### Phase II (SQLModel)
When migrating to SQLModel in Phase II:
- Keep the same field names and types
- Convert `datetime` to `DateTime` field
- Add `table_name = "tasks"` metadata
- Keep validation logic

### Conversion Example
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        table_name = "tasks"
```

## Best Practices

1. **Always validate input** before creating tasks
2. **Use `strip()`** to clean whitespace from text fields
3. **Handle empty descriptions** gracefully
4. **Display dates** in user-friendly format
5. **Use IDs** for all operations (not titles)
6. **Never expose internal IDs** to users as editable fields