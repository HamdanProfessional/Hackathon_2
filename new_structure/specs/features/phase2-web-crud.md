# Phase II: Web CRUD Application Specification

## Overview
Phase II evolves the console application into a full-stack web application with intermediate features. This phase introduces persistent storage through Neon PostgreSQL, user authentication, and enhanced task management capabilities.

## Scope: Intermediate Level (Enhanced Features)

This phase builds upon the basic CRUD operations from Phase I and adds:
1. **Priorities** - High/Medium/Low priority levels with visual indicators
2. **Tags/Categories** - Organize tasks with custom tags and categories
3. **Search & Filter** - Find tasks quickly with text search and filters
4. **Sort Tasks** - Arrange tasks by various criteria (date, priority, title)
5. **Due Dates** - Set and track task deadlines
6. **Task Statistics** - Visual dashboard with completion metrics
7. **Responsive Design** - Mobile-friendly interface

## User Stories

### Story 1: Task Priorities
**As a** user
**I want to** set priority levels on my tasks
**So that** I can focus on what's most important

**Acceptance Criteria:**
- User can select High, Medium, or Low priority when creating/editing tasks
- Priority levels have distinct visual indicators (colors, icons)
- Tasks can be sorted by priority
- Default priority is Medium for new tasks
- Priority is clearly visible in the task list

### Story 2: Tags and Categories
**As a** user
**I want to** organize my tasks with tags
**So that** I can group related tasks together

**Acceptance Criteria:**
- User can add multiple tags to each task
- Tags are displayed as colored badges/chips
- User can filter tasks by tag
- Tag suggestions appear based on existing tags
- User can create custom tags on the fly
- Maximum 10 tags per task to prevent clutter

### Story 3: Search Functionality
**As a** user
**I want to** search through my tasks
**So that** I can quickly find specific tasks

**Acceptance Criteria:**
- Search works across task title and description
- Search is case-insensitive
- Results update in real-time as user types
- Search highlights matching text
- Search can be combined with filters
- Empty search shows all tasks

### Story 4: Advanced Filtering
**As a** user
**I want to** filter tasks by various criteria
**So that** I can view specific subsets of tasks

**Acceptance Criteria:**
- Filter by completion status (completed/pending)
- Filter by priority level
- Filter by tag(s)
- Filter by due date (overdue, today, this week, this month)
- Multiple filters can be combined
- Clear all filters option
- Active filters are visually indicated

### Story 5: Due Date Management
**As a** user
**I want to** set due dates for my tasks
**So that** I can track deadlines

**Acceptance Criteria:**
- Date picker for setting due dates
- Due date is displayed in task list and details
- Overdue tasks are visually highlighted
- Tasks due today are specially marked
- Tasks can be sorted by due date
- Due date is optional (can be left blank)

### Story 6: Task Statistics Dashboard
**As a** user
**I want to** see statistics about my tasks
**So that** I can track my productivity

**Acceptance Criteria:**
- Total tasks count
- Completed vs pending ratio
- Tasks by priority level distribution
- Tasks due this week
- Recent activity timeline
- Completion rate over time

### Story 7: Responsive Design
**As a** user
**I want to** access the app on my mobile device
**So that** I can manage tasks on the go

**Acceptance Criteria:**
- Mobile-optimized layout
- Touch-friendly buttons and controls
- Readable text on small screens
- Collapsible navigation on mobile
- Swipe gestures for task actions

## Technical Implementation

### Frontend Architecture (Next.js 16)

#### Directory Structure
```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── dashboard/
│   │   │   ├── page.tsx
│   │   │   └── components/
│   │   ├── tasks/
│   │   │   ├── page.tsx
│   │   │   ├── [id]/
│   │   │   └── components/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/              # Shadcn/ui components
│   │   ├── forms/
│   │   ├── charts/
│   │   └── layout/
│   ├── lib/
│   │   ├── api.ts          # API client
│   │   ├── auth.ts         # Authentication helpers
│   │   └── utils.ts
│   ├── hooks/              # Custom React hooks
│   ├── types/              # TypeScript type definitions
│   └── styles/             # Additional CSS modules
```

#### Core Components

**TaskList Component**
```typescript
// frontend/src/components/tasks/TaskList.tsx
import { Task, TaskFilter, TaskSort } from '@/types'
import { TaskCard } from './TaskCard'
import { TaskSkeleton } from './TaskSkeleton'

interface TaskListProps {
  tasks: Task[]
  loading?: boolean
  filter: TaskFilter
  sort: TaskSort
  onTaskUpdate: (id: string, updates: Partial<Task>) => void
  onTaskDelete: (id: string) => void
}

export function TaskList({ tasks, loading, filter, sort, onTaskUpdate, onTaskDelete }: TaskListProps) {
  if (loading) {
    return <TaskSkeleton count={5} />
  }

  const filteredAndSortedTasks = tasks
    .filter(task => {
      // Apply filters
      if (filter.status && filter.status !== 'all' && task.completed !== (filter.status === 'completed')) {
        return false
      }
      if (filter.priority && task.priority !== filter.priority) {
        return false
      }
      if (filter.tags?.length && !filter.tags.some(tag => task.tags.includes(tag))) {
        return false
      }
      if (filter.search) {
        const searchLower = filter.search.toLowerCase()
        return task.title.toLowerCase().includes(searchLower) ||
               task.description?.toLowerCase().includes(searchLower)
      }
      return true
    })
    .sort((a, b) => {
      // Apply sorting
      switch (sort.field) {
        case 'dueDate':
          return (a.dueDate?.getTime() || 0) - (b.dueDate?.getTime() || 0)
        case 'priority':
          const priorityOrder = { high: 0, medium: 1, low: 2 }
          return priorityOrder[a.priority] - priorityOrder[b.priority]
        case 'title':
          return a.title.localeCompare(b.title)
        case 'createdAt':
        default:
          return b.createdAt.getTime() - a.createdAt.getTime()
      }
    })

  return (
    <div className="space-y-2">
      {filteredAndSortedTasks.map(task => (
        <TaskCard
          key={task.id}
          task={task}
          onUpdate={onTaskUpdate}
          onDelete={onTaskDelete}
        />
      ))}
      {filteredAndSortedTasks.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No tasks found matching your criteria
        </div>
      )}
    }
  </div>
)
}
```

**TaskCard Component**
```typescript
// frontend/src/components/tasks/TaskCard.tsx
import { Task } from '@/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Calendar, Clock, Tag, Trash2, Edit } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

interface TaskCardProps {
  task: Task
  onUpdate: (id: string, updates: Partial<Task>) => void
  onDelete: (id: string) => void
}

export function TaskCard({ task, onUpdate, onDelete }: TaskCardProps) {
  const isOverdue = task.dueDate && task.dueDate < new Date() && !task.completed
  const isDueToday = task.dueDate &&
    task.dueDate.toDateString() === new Date().toDateString()

  const priorityColors = {
    high: 'bg-red-100 text-red-800 border-red-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200'
  }

  return (
    <div className={`border rounded-lg p-4 transition-all hover:shadow-md ${
      task.completed ? 'bg-gray-50 opacity-75' : 'bg-white'
    } ${isOverdue ? 'border-red-300' : 'border-gray-200'}`}>
      <div className="flex items-start gap-3">
        <Checkbox
          checked={task.completed}
          onCheckedChange={(checked) => onUpdate(task.id, { completed: !!checked })}
          className="mt-1"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className={`font-medium truncate ${
              task.completed ? 'line-through text-gray-500' : 'text-gray-900'
            }`}>
              {task.title}
            </h3>
            <Badge variant="outline" className={priorityColors[task.priority]}>
              {task.priority}
            </Badge>
          </div>

          {task.description && (
            <p className="text-sm text-gray-600 mb-2 line-clamp-2">
              {task.description}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
            {task.dueDate && (
              <div className={`flex items-center gap-1 ${
                isOverdue ? 'text-red-600 font-medium' : isDueToday ? 'text-blue-600 font-medium' : ''
              }`}>
                <Calendar className="w-3 h-3" />
                {task.dueDate.toLocaleDateString()}
                {isOverdue && ' (Overdue)'}
                {isDueToday && ' (Today)'}
              </div>
            )}

            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatDistanceToNow(task.createdAt, { addSuffix: true })}
            </div>

            {task.tags.length > 0 && (
              <div className="flex items-center gap-1">
                <Tag className="w-3 h-3" />
                <div className="flex gap-1">
                  {task.tags.slice(0, 3).map(tag => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {task.tags.length > 3 && (
                    <span className="text-gray-400">+{task.tags.length - 3}</span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {/* Open edit modal */}}
          >
            <Edit className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(task.id)}
            className="text-red-600 hover:text-red-700"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
```

**TaskForm Component**
```typescript
// frontend/src/components/forms/TaskForm.tsx
import { useState } from 'react'
import { Task, TaskPriority } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { X, Plus } from 'lucide-react'

interface TaskFormProps {
  task?: Task
  onSubmit: (data: Partial<Task>) => void
  onCancel: () => void
}

export function TaskForm({ task, onSubmit, onCancel }: TaskFormProps) {
  const [formData, setFormData] = useState({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || TaskPriority.MEDIUM,
    dueDate: task?.dueDate?.toISOString().split('T')[0] || '',
    tags: task?.tags || []
  })
  const [newTag, setNewTag] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      ...formData,
      dueDate: formData.dueDate ? new Date(formData.dueDate) : null
    })
  }

  const addTag = () => {
    if (newTag.trim() && formData.tags.length < 10) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim().toLowerCase()]
      }))
      setNewTag('')
    }
  }

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Title *</label>
        <Input
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          placeholder="Enter task title"
          required
          maxLength={255}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Description</label>
        <Textarea
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          placeholder="Enter task description (optional)"
          rows={3}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Priority</label>
          <Select
            value={formData.priority}
            onValueChange={(value) => setFormData(prev => ({ ...prev, priority: value as TaskPriority }))}
          >
            <Select.Option value={TaskPriority.HIGH}>High</Select.Option>
            <Select.Option value={TaskPriority.MEDIUM}>Medium</Select.Option>
            <Select.Option value={TaskPriority.LOW}>Low</Select.Option>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Due Date</label>
          <Input
            type="date"
            value={formData.dueDate}
            onChange={(e) => setFormData(prev => ({ ...prev, dueDate: e.target.value }))}
            min={new Date().toISOString().split('T')[0]}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Tags</label>
        <div className="flex gap-2 mb-2">
          <Input
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            placeholder="Add a tag"
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
            disabled={formData.tags.length >= 10}
          />
          <Button
            type="button"
            variant="outline"
            onClick={addTag}
            disabled={!newTag.trim() || formData.tags.length >= 10}
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>
        {formData.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {formData.tags.map(tag => (
              <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="ml-1 hover:bg-gray-200 rounded"
                >
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}
        <p className="text-xs text-gray-500 mt-1">
          {formData.tags.length}/10 tags
        </p>
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={!formData.title.trim()}>
          {task ? 'Update Task' : 'Create Task'}
        </Button>
      </div>
    </form>
  )
}
```

### Backend Architecture (FastAPI)

#### API Endpoints
```python
# backend/app/api/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.crud.task import task_crud
from app.api.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None, regex="^(completed|pending|all)$"),
    priority: Optional[str] = Query(None, regex="^(high|medium|low)$"),
    tags: Optional[List[str]] = Query(None),
    sort_by: Optional[str] = Query("createdAt", regex="^(createdAt|dueDate|priority|title)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's tasks with filtering and sorting."""
    tasks = task_crud.get_multi_with_filters(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        status=status,
        priority=priority,
        tags=tags,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return tasks

@router.post("/", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new task."""
    task = task_crud.create_with_user(db=db, obj_in=task_data, user_id=current_user.id)
    return task

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific task."""
    task = task_crud.get_user_task(db=db, id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a task."""
    task = task_crud.get_user_task(db=db, id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_crud.update(db=db, db_obj=task, obj_in=task_data)
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a task."""
    task = task_crud.get_user_task(db=db, id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_crud.remove(db=db, id=task_id)
    return {"message": "Task deleted successfully"}
```

#### CRUD Operations
```python
# backend/app/crud/task.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

class TaskCRUD:
    def get_user_task(self, db: Session, *, id: str, user_id: str) -> Optional[Task]:
        """Get a task belonging to a specific user."""
        return db.query(Task).filter(and_(Task.id == id, Task.user_id == user_id)).first()

    def get_multi_with_filters(
        self,
        db: Session,
        *,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = "createdAt",
        sort_order: str = "desc"
    ) -> List[Task]:
        """Get tasks with advanced filtering and sorting."""
        query = db.query(Task).filter(Task.user_id == user_id)

        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term)
                )
            )

        # Status filter
        if status == "completed":
            query = query.filter(Task.completed == True)
        elif status == "pending":
            query = query.filter(Task.completed == False)

        # Priority filter
        if priority:
            query = query.filter(Task.priority == priority)

        # Tags filter (tasks must have ALL specified tags)
        if tags:
            for tag in tags:
                query = query.filter(Task.tags.contains([tag]))

        # Sorting
        sort_column = getattr(Task, sort_by, Task.createdAt)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        return query.offset(skip).limit(limit).all()

    def create_with_user(self, db: Session, *, obj_in: TaskCreate, user_id: str) -> Task:
        """Create a task for a specific user."""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        db_obj = Task(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Task, obj_in: TaskUpdate) -> Task:
        """Update a task."""
        obj_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: str) -> Task:
        """Delete a task."""
        obj = db.query(Task).get(id)
        db.delete(obj)
        db.commit()
        return obj

task_crud = TaskCRUD()
```

#### Pydantic Schemas
```python
# backend/app/schemas/task.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    completed: bool = False
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: List[str] = Field(default_factory=list, max_items=10)
    due_date: Optional[datetime] = None

    @validator('tags')
    def validate_tags(cls, v):
        return [tag.strip().lower() for tag in v if tag.strip()]

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[TaskPriority] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            return [tag.strip().lower() for tag in v if tag.strip()]
        return v

class TaskResponse(TaskBase):
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float
    high_priority_tasks: int
    overdue_tasks: int
    tasks_due_today: int
    tasks_due_this_week: int
```

### Database Models
```python
# backend/app/models/task.py
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from uuid import uuid4
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String, default=None)
    completed = Column(Boolean, default=False)
    priority = Column(String(20), default="medium")
    tags = Column(JSON, default=list)
    due_date = Column(DateTime(timezone=True), default=None)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"
```

## Testing Strategy

### Frontend Tests
```typescript
// frontend/src/components/tasks/__tests__/TaskList.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { TaskList } from '../TaskList'
import { Task, TaskFilter, TaskSort } from '@/types'

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Test task 1',
    description: 'Description 1',
    completed: false,
    priority: 'high',
    tags: ['work', 'urgent'],
    dueDate: new Date(),
    createdAt: new Date(),
    updatedAt: new Date()
  },
  // ... more test tasks
]

describe('TaskList', () => {
  it('renders tasks correctly', () => {
    render(
      <TaskList
        tasks={mockTasks}
        filter={{} as TaskFilter}
        sort={{ field: 'createdAt', order: 'desc' } as TaskSort}
        onTaskUpdate={jest.fn()}
        onTaskDelete={jest.fn()}
      />
    )

    expect(screen.getByText('Test task 1')).toBeInTheDocument()
  })

  it('filters tasks by search term', async () => {
    const onTaskUpdate = jest.fn()
    const { rerender } = render(
      <TaskList
        tasks={mockTasks}
        filter={{ search: 'urgent' } as TaskFilter}
        sort={{ field: 'createdAt', order: 'desc' } as TaskSort}
        onTaskUpdate={onTaskUpdate}
        onTaskDelete={jest.fn()}
      />
    )

    await waitFor(() => {
      expect(screen.getByText('Test task 1')).toBeInTheDocument()
    })
  })

  it('sorts tasks by priority', () => {
    // Test sorting functionality
  })
})
```

### Backend Tests
```python
# backend/tests/test_tasks.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.task import Task

client = TestClient(app)

@pytest.fixture
def test_user(db: Session):
    user = User(user_id="testuser", email="test@example.com", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    # Generate JWT token for test user
    token = create_access_token(data={"sub": test_user.user_id})
    return {"Authorization": f"Bearer {token}"}

def test_create_task(auth_headers):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "priority": "high",
        "tags": ["test", "important"]
    }

    response = client.post("/tasks/", json=task_data, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["priority"] == task_data["priority"]
    assert set(data["tags"]) == set(task_data["tags"])

def test_get_tasks_with_filters(auth_headers, test_user):
    # Create test tasks
    # Test filtering by priority
    response = client.get("/tasks/?priority=high", headers=auth_headers)
    assert response.status_code == 200

    tasks = response.json()
    for task in tasks:
        assert task["priority"] == "high"

    # Test search functionality
    response = client.get("/tasks/?search=urgent", headers=auth_headers)
    assert response.status_code == 200

def test_update_task(auth_headers, test_user):
    # Create a task first
    task = Task(
        title="Original Title",
        priority="medium",
        user_id=test_user.user_id
    )
    db.add(task)
    db.commit()

    update_data = {
        "title": "Updated Title",
        "priority": "high"
    }

    response = client.put(f"/tasks/{task.id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["priority"] == update_data["priority"]
```

## Performance Requirements

### Frontend Performance
- Initial page load: < 3 seconds
- Task list rendering: < 100ms for 100 tasks
- Search response: < 50ms
- Filter application: < 100ms
- Bundle size: < 500KB (gzipped)

### Backend Performance
- API response time: < 200ms (95th percentile)
- Database queries: < 50ms (indexed queries)
- Concurrent users: Support 100+ simultaneous users
- Memory usage: < 512MB per container

### Database Optimization
```sql
-- Recommended indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

## Security Considerations

### Authentication & Authorization
- All endpoints require JWT authentication
- Users can only access their own tasks
- Rate limiting on API endpoints
- CORS configured for production domains

### Input Validation
- Server-side validation for all inputs
- SQL injection prevention through SQLAlchemy ORM
- XSS prevention in frontend
- CSRF protection on state-changing endpoints

### Data Protection
- Password hashing with bcrypt
- Secure JWT token storage
- HTTPS in production
- Environment variables for secrets

## Success Metrics

### User Engagement
- Daily active users
- Task completion rate
- Feature adoption (priorities, tags, search)
- Session duration

### Technical Metrics
- API response times
- Error rates
- Database query performance
- Frontend bundle size

### Business KPIs
- User retention rate
- Task creation frequency
- Feature utilization
- User satisfaction score

## Out of Scope

### Features Not in Phase II
- AI-powered features (Phase III)
- Real-time collaboration
- File attachments
- Task templates
- Advanced reporting/analytics
- Email notifications
- Mobile apps (native)
- Integration with third-party services

### Technical Limitations
- Single-user tasks only (no sharing)
- No task dependencies
- No recurring tasks
- No time tracking
- No calendar integration

## Dependencies

### Frontend
- Next.js 16
- React 18
- TypeScript 5
- Tailwind CSS 3
- Shadcn/ui components
- Lucide React (icons)
- date-fns (date utilities)
- React Hook Form
- Zod (validation)

### Backend
- Python 3.13+
- FastAPI
- SQLModel
- Alembic
- Better Auth
- PostgreSQL (Neon)
- Pydantic
- pytest
- Uvicorn

This Phase II specification provides a comprehensive foundation for an intermediate-level web application with enhanced features while maintaining clean architecture and performance standards.