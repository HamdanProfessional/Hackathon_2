# Data Model: AI-Powered Todo Chatbot

**Date**: 2025-12-13
**Phase**: 1 - Design
**Purpose**: Database schema extensions for conversation persistence

## Overview

Phase III extends the existing Phase II database schema with two new tables to support conversational AI functionality while preserving all existing tables unchanged.

**Existing Tables** (Phase II - unchanged):
- `users` - User authentication and profiles
- `tasks` - Todo items with user ownership

**New Tables** (Phase III):
- `conversations` - Chat sessions between users and AI
- `messages` - Individual messages within conversations

## Schema Diagram

```
users (existing)
  ├─→ tasks (existing, one-to-many)
  └─→ conversations (NEW, one-to-many)
       └─→ messages (NEW, one-to-many)
```

## Table Definitions

### conversations

Represents a chat session between a user and the AI assistant.

**Columns**:

| Column       | Type                     | Constraints              | Description                           |
|--------------|--------------------------|--------------------------|---------------------------------------|
| id           | SERIAL                   | PRIMARY KEY              | Auto-incrementing conversation ID     |
| user_id      | INTEGER                  | NOT NULL, FOREIGN KEY    | References users.id                   |
| created_at   | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW()  | When conversation was started         |
| updated_at   | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW()  | Last message timestamp (auto-updated) |

**Indexes**:
- `idx_conversations_user_id` on `user_id` (for listing user's conversations)
- `idx_conversations_updated_at` on `updated_at` (for sorting by recency)

**Foreign Keys**:
- `user_id` → `users.id` (ON DELETE CASCADE - delete conversations when user deleted)

**SQL Definition**:
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);
```

**Business Rules**:
- Each conversation belongs to exactly one user
- Users can have multiple conversations (unlimited)
- Conversations never shared between users (strict data isolation)
- `updated_at` automatically updated when new message added (trigger)

---

### messages

Stores individual messages (user inputs and AI responses) within conversations.

**Columns**:

| Column           | Type                     | Constraints              | Description                                |
|------------------|--------------------------|--------------------------|--------------------------------------------|
| id               | SERIAL                   | PRIMARY KEY              | Auto-incrementing message ID               |
| conversation_id  | INTEGER                  | NOT NULL, FOREIGN KEY    | References conversations.id                |
| role             | VARCHAR(20)              | NOT NULL, CHECK          | Either 'user' or 'assistant'               |
| content          | TEXT                     | NOT NULL                 | Message content (natural language or JSON) |
| created_at       | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW()  | When message was created                   |

**Indexes**:
- `idx_messages_conversation_created` on `(conversation_id, created_at)` (composite index for ordered retrieval)

**Foreign Keys**:
- `conversation_id` → `conversations.id` (ON DELETE CASCADE - delete messages when conversation deleted)

**Constraints**:
- `CHECK (role IN ('user', 'assistant'))` - Enforce valid role values

**SQL Definition**:
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

**Business Rules**:
- Each message belongs to exactly one conversation
- Messages ordered chronologically within conversation
- `role='user'` for user input messages
- `role='assistant'` for AI-generated responses
- `content` stores plain text for both roles
- Messages immutable once created (no updates, only inserts)

---

## Database Trigger: Update conversation.updated_at

Automatically update `conversations.updated_at` timestamp when new message added:

```sql
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = NEW.created_at
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();
```

**Purpose**: Enables sorting conversations by "most recent activity" without complex joins.

---

## Relationships

### User ← Conversation (One-to-Many)

- One user can have many conversations
- Each conversation belongs to exactly one user
- Cascade delete: Deleting user deletes all their conversations

**Query Examples**:
```sql
-- Get all conversations for a user (sorted by most recent)
SELECT * FROM conversations
WHERE user_id = $1
ORDER BY updated_at DESC;

-- Count user's conversations
SELECT COUNT(*) FROM conversations WHERE user_id = $1;
```

### Conversation ← Message (One-to-Many)

- One conversation contains many messages
- Each message belongs to exactly one conversation
- Cascade delete: Deleting conversation deletes all its messages

**Query Examples**:
```sql
-- Load conversation history (most recent 50 messages)
SELECT role, content, created_at
FROM messages
WHERE conversation_id = $1
ORDER BY created_at DESC
LIMIT 50;

-- Load messages paginated (before a certain message ID)
SELECT role, content, created_at
FROM messages
WHERE conversation_id = $1 AND id < $2
ORDER BY created_at DESC
LIMIT 50;
```

---

## Data Isolation

**User-level isolation** enforced through application layer and database constraints:

1. **Conversations**: All queries filter by `user_id` from authenticated session
2. **Messages**: Accessed only through conversation_id (which already belongs to user)
3. **Foreign keys**: Ensure referential integrity (no orphaned messages)

**Example isolation check**:
```python
async def get_conversation(conversation_id: int, user_id: int) -> Conversation:
    # Validate conversation belongs to user
    conversation = await db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise NotFoundException("Conversation not found")
    return conversation
```

---

## Storage Estimates

**Assumptions**:
- Average conversation: 20 messages (10 user + 10 assistant)
- Average message length: 200 characters
- 1000 users, each with 5 conversations

**Calculations**:

**conversations table**:
- Row size: ~40 bytes (id + user_id + timestamps)
- 1000 users × 5 conversations = 5,000 rows
- Storage: ~200 KB + indexes ~100 KB = **~300 KB**

**messages table**:
- Row size: ~250 bytes (id + conversation_id + role + content + timestamp)
- 5,000 conversations × 20 messages = 100,000 rows
- Storage: ~25 MB + indexes ~10 MB = **~35 MB**

**Total Phase III storage**: ~35.3 MB (negligible compared to potential task data growth)

**Growth projections**:
- Linear with conversation volume
- Can archive old conversations to cold storage if needed
- Indexes scale logarithmically (O(log n) lookups)

---

## Migration Strategy

**Alembic Migration File**: `backend/alembic/versions/xxx_add_conversations.py`

**Migration Steps**:
1. Create `conversations` table
2. Create `messages` table
3. Create indexes on both tables
4. Create trigger for `updated_at` automation
5. No data migration needed (Phase III is additive)

**Rollback Strategy**:
1. Drop trigger
2. Drop indexes
3. Drop `messages` table (cascade handles foreign keys)
4. Drop `conversations` table

**Zero Downtime**: Migration is purely additive - existing Phase II functionality unaffected.

---

## SQLAlchemy Models

**Conversation Model** (`backend/app/models/conversation.py`):
```python
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
```

**Message Model** (`backend/app/models/message.py`):
```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="check_role_values"),
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
```

**User Model Extension** (`backend/app/models/user.py`):
```python
# Add to existing User model:
conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
```

---

## Query Patterns

### Common Operations

**1. Create new conversation**:
```python
conversation = Conversation(user_id=current_user.id)
await db.add(conversation)
await db.commit()
```

**2. Add message to conversation**:
```python
message = Message(
    conversation_id=conversation_id,
    role="user",  # or "assistant"
    content="User's message text"
)
await db.add(message)
await db.commit()
# Trigger automatically updates conversation.updated_at
```

**3. Load conversation history**:
```python
messages = await db.execute(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.asc())
    .limit(50)
)
```

**4. List user's conversations** (sorted by recent activity):
```python
conversations = await db.execute(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.updated_at.desc())
)
```

**5. Delete conversation** (cascade deletes all messages):
```python
await db.delete(conversation)
await db.commit()
# All messages automatically deleted via CASCADE
```

---

## Validation Rules

### Conversation Validation

- `user_id` must reference existing user
- Cannot create conversation for different user than authenticated user
- Conversation IDs are auto-generated (never user-provided)

### Message Validation

- `conversation_id` must reference existing conversation
- Conversation must belong to current user (validated before message creation)
- `role` must be exactly "user" or "assistant" (enforced by CHECK constraint)
- `content` cannot be empty string (minimum length: 1 character)
- `content` maximum length: 10,000 characters (prevent abuse)

---

## Performance Considerations

**Optimizations**:
1. Composite index `(conversation_id, created_at)` enables fast ordered retrieval without sorting
2. `user_id` index on conversations supports fast user conversation lookups
3. Cascade deletes prevent orphaned records without application logic
4. Trigger-based `updated_at` avoids manual timestamp management

**Future Optimizations** (if needed):
- Partition messages table by creation date for very large datasets
- Add full-text search index on `content` for conversation search
- Archive conversations older than 6 months to separate table
- Implement read replicas for conversation history queries

---

## References

- Phase II Data Model: `specs/002-web-app/data-model.md` (users, tasks tables)
- Alembic Migrations: `backend/alembic/versions/`
- SQLAlchemy Relationships: https://docs.sqlalchemy.org/en/14/orm/relationships.html
