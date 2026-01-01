# API Schema Sync Examples

Type conversion between Python Pydantic and TypeScript.

## Type Conversion Map

| Python Type | TypeScript Type | Notes |
|------------|-----------------|-------|
| `int` | `number` | |
| `str` | `string` | |
| `bool` | `boolean` | |
| `float` | `number` | |
| `datetime` | `string` | ISO 8601 format |
| `UUID` | `string` | |
| `Optional[T]` | `T \| null` | |
| `List[T]` | `T[]` | |
| `Dict[K, V]` | `Record<K, V>` | |
| `Literal["a","b"]` | `"a" \| "b"` | Union type |
| `Enum` | `enum` | Convert to TS enum |

## Complete Example

**Backend (Pydantic)**:

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class TaskResponse(BaseModel):
    id: int
    user_id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Frontend (TypeScript)**:

```typescript
export enum TaskStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed"
}

export enum TaskPriority {
  LOW = "low",
  NORMAL = "normal",
  HIGH = "high"
}

export interface Task {
  id: number;
  user_id: string;  // UUID as string
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;  // ISO datetime string
  tags: string[];
  created_at: string;
  updated_at: string;
}

// Create schema (no user_id, timestamps)
export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string[];
}

// Update schema (all optional)
export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string[];
}
```
