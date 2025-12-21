# Database Schema Specification
## Neon Serverless PostgreSQL with SQLModel

This specification defines the complete database schema for the Todo Evolution application using SQLModel on Neon Serverless PostgreSQL.

## Table Definitions

### 1. Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    tags JSONB DEFAULT '[]',
    due_date TIMESTAMP,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_pattern VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**SQLModel Implementation:**
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    completed: bool = False
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    is_recurring: bool = False
    recurring_pattern: Optional[str] = None

class Task(TaskBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for API endpoints",
                "priority": "high",
                "tags": ["work", "documentation"],
                "due_date": "2025-12-25T23:59:59Z"
            }
        }
```

**Indexes for Performance:**
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
```

### 2. Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**SQLModel Implementation:**
```python
class UserBase(SQLModel):
    user_id: str = Field(unique=True, max_length=255)
    email: str = Field(unique=True, max_length=255)
    name: Optional[str] = None

class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List[Task] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "email": "user@example.com",
                "name": "John Doe"
            }
        }
```

### 3. Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**SQLModel Implementation:**
```python
class ConversationBase(SQLModel):
    title: Optional[str] = None

class Conversation(ConversationBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Task Management Chat"
            }
        }
```

### 4. Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**SQLModel Implementation:**
```python
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class MessageBase(SQLModel):
    role: MessageRole
    content: str

class Message(MessageBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str
    conversation_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: User = Relationship(back_populates="messages")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What tasks do I have due today?"
            }
        }
```

## Database Relationships

```python
# Complete relationship definitions in the main models file

# In User model
tasks: List[Task] = Relationship(back_populates="user")
conversations: List[Conversation] = Relationship(back_populates="user")
messages: List[Message] = Relationship(back_populates="user")

# In Conversation model
user: User = Relationship(back_populates="conversations")
messages: List[Message] = Relationship(back_populates="conversation", cascade_delete=True)

# In Message model
conversation: Conversation = Relationship(back_populates="messages")
user: User = Relationship(back_populates="messages")

# In Task model
user: User = Relationship(back_populates="tasks")
```

## Migration Strategy

### Initial Migration (Alembic)
```python
# alembic/versions/001_initial_schema.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('email')
    )

    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False),
        sa.Column('recurring_pattern', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("priority IN ('high', 'medium', 'low')", name='check_priority')
    )

    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create messages table
    op.create_table('messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_role')
    )

    # Create indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_user_completed', 'tasks', ['user_id', 'completed'])
    op.create_index('idx_tasks_user_priority', 'tasks', ['user_id', 'priority'])
    op.create_index('idx_tasks_due_date', 'tasks', ['due_date'], unique=False, postgresql_where=sa.text('due_date IS NOT NULL'))
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('tasks')
    op.drop_table('users')
```

## Data Validation Rules

### Task Validation
```python
from pydantic import validator

class TaskCreate(TaskBase):
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return [tag.strip() for tag in v if tag.strip()]

    @validator('recurring_pattern')
    def validate_recurring_pattern(cls, v, values):
        if values.get('is_recurring') and not v:
            raise ValueError('Recurring pattern required when is_recurring is True')
        return v
```

### Constraints Summary

| Table | Constraints |
|-------|-------------|
| tasks | user_id (FK), title (not null), priority (enum), tags (JSON array) |
| users | user_id (unique), email (unique) |
| conversations | user_id (FK) |
| messages | user_id (FK), conversation_id (FK), role (enum) |

## Performance Optimization

### Recommended Indexes
1. `idx_tasks_user_id` - Primary user lookup
2. `idx_tasks_user_completed` - Filter by completion status
3. `idx_tasks_user_priority` - Sort by priority
4. `idx_tasks_due_date` - Filter by due date
5. `idx_messages_conversation_created` - Conversation history retrieval
6. `idx_tasks_tags` - Tag-based filtering (GIN index)

### Connection Pool Configuration
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False
)
```

This schema provides a solid foundation for all phases of the Todo Evolution project, supporting basic CRUD operations in Phase I, enhanced features in Phase II, and full AI chatbot capabilities in Phase III.