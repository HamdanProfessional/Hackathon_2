# Phase III AI Chatbot - Database Migration Summary

## Migration: Update Chat Schema for tool_calls Support

**Migration File**: `backend/alembic/versions/003_update_chat_schema_for_tool_calls.py`

**Revision ID**: 003

**Revises**: 69ef5db393b3

**Date**: 2025-12-20

---

## Changes Implemented

### Task 1: SQLModel Updates

#### Conversation Model (`backend/app/models/conversation.py`)

**Changes**:
1. Changed `id` from `Integer` to `UUID(as_uuid=True)` with `uuid4` default
2. Added `title` field: `String(200)`, default="New Conversation"
3. Added index on `created_at DESC` for efficient sorting

**Before**:
```python
id = Column(Integer, primary_key=True, index=True)
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
# No title field
created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
```

**After**:
```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4, index=True)
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
title = Column(String(200), nullable=False, default="New Conversation", server_default="New Conversation")
created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)

__table_args__ = (
    Index('idx_conversations_created_at_desc', 'created_at', postgresql_ops={'created_at': 'DESC'}),
)
```

#### Message Model (`backend/app/models/message.py`)

**Changes**:
1. Changed `id` from `Integer` to `UUID(as_uuid=True)` with `uuid4` default
2. Changed `conversation_id` from `Integer` FK to `UUID(as_uuid=True)` FK
3. Added `tool_calls` field: `JSON` (nullable) - stores OpenAI tool_calls format
4. Added `tool_call_id` field: `String(100)` (nullable)
5. Added `name` field: `String(100)` (nullable)
6. Updated `role` constraint to include 'system' and 'tool' (in addition to 'user'/'assistant')
7. Added index on `role` for efficient filtering
8. Existing composite index `(conversation_id, created_at ASC)` remains

**Before**:
```python
id = Column(Integer, primary_key=True, index=True)
conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
role = Column(String(20), nullable=False)
content = Column(Text, nullable=False)
created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

__table_args__ = (
    CheckConstraint("role IN ('user', 'assistant')", name="check_role_values"),
    Index("idx_messages_conversation_created", "conversation_id", "created_at"),
)
```

**After**:
```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4, index=True)
conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
role = Column(String(20), nullable=False, index=True)
content = Column(Text, nullable=False)
tool_calls = Column(JSON, nullable=True)  # OpenAI tool_calls format
tool_call_id = Column(String(100), nullable=True)  # For tool role messages
name = Column(String(100), nullable=True)  # For tool role messages
created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

__table_args__ = (
    CheckConstraint("role IN ('user', 'assistant', 'system', 'tool')", name="check_role_values"),
    Index("idx_messages_conversation_created", "conversation_id", "created_at"),
)
```

---

### Task 2: Alembic Migration

#### Migration Strategy

**IMPORTANT**: This migration is destructive because changing primary key types from Integer to UUID requires recreating the tables.

**Strategy**:
1. Drop existing `messages` table (due to foreign key dependency)
2. Drop existing `conversations` table
3. Recreate `conversations` table with UUID primary key and new fields
4. Recreate `messages` table with UUID primary key and new fields
5. Recreate all indexes and constraints
6. Recreate database triggers

**Data Loss**: This migration will DROP all existing conversations and messages. If production data exists, backup before running.

#### Migration Details

**Upgrade Process** (`alembic upgrade head`):
```sql
-- 1. Drop existing structures
DROP TRIGGER IF EXISTS trigger_update_conversation_timestamp ON messages;
DROP FUNCTION IF EXISTS update_conversation_timestamp();
DROP TABLE messages;
DROP TABLE conversations;

-- 2. Recreate conversations with UUID
CREATE TABLE conversations (
    id UUID NOT NULL,
    user_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Create indexes
CREATE INDEX ix_conversations_id ON conversations(id);
CREATE INDEX ix_conversations_user_id ON conversations(user_id);
CREATE INDEX ix_conversations_updated_at ON conversations(updated_at);
CREATE INDEX idx_conversations_created_at_desc ON conversations(created_at DESC);

-- 4. Recreate messages with UUID and new fields
CREATE TABLE messages (
    id UUID NOT NULL,
    conversation_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSON NULL,
    tool_call_id VARCHAR(100) NULL,
    name VARCHAR(100) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    CHECK (role IN ('user', 'assistant', 'system', 'tool'))
);

-- 5. Create indexes
CREATE INDEX ix_messages_id ON messages(id);
CREATE INDEX ix_messages_role ON messages(role);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);

-- 6. Recreate triggers
CREATE FUNCTION update_conversation_timestamp() RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations SET updated_at = NEW.created_at WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();
```

**Downgrade Process** (`alembic downgrade -1`):
- Reverses all changes
- Recreates tables with Integer primary keys
- Restores original schema without tool_calls fields

---

## Verification

### Database Schema Verification

All requirements verified successfully:

#### Conversations Table
- [OK] id: UUID (NOT NULL)
- [OK] user_id: UUID (NOT NULL)
- [OK] title: VARCHAR(200) (NOT NULL, default='New Conversation')
- [OK] created_at: TIMESTAMP (NOT NULL)
- [OK] updated_at: TIMESTAMP (NOT NULL)
- [OK] Index: idx_conversations_created_at_desc

#### Messages Table
- [OK] id: UUID (NOT NULL)
- [OK] conversation_id: UUID (NOT NULL, FK to conversations.id)
- [OK] role: VARCHAR(20) (NOT NULL, CHECK constraint includes 'user', 'assistant', 'system', 'tool')
- [OK] content: TEXT (NOT NULL)
- [OK] tool_calls: JSON (NULLABLE) - stores OpenAI tool_calls format
- [OK] tool_call_id: VARCHAR(100) (NULLABLE)
- [OK] name: VARCHAR(100) (NULLABLE)
- [OK] created_at: TIMESTAMP (NOT NULL)
- [OK] Index: idx_messages_conversation_created (conversation_id, created_at)
- [OK] Index: ix_messages_role

### tool_calls JSON Format

The `tool_calls` column stores OpenAI tool call format:

```json
[
  {
    "id": "call_abc123",
    "type": "function",
    "function": {
      "name": "add_task",
      "arguments": "{\"user_id\": \"uuid-string\", \"title\": \"Buy groceries\"}"
    }
  }
]
```

This allows the stateless agent to reconstruct exact conversation state including tool calls.

---

## Testing Results

### Migration Tests

1. **Upgrade Test**: PASSED
   ```bash
   alembic upgrade 003
   # Result: Tables recreated with UUID primary keys and new fields
   ```

2. **Downgrade Test**: PASSED
   ```bash
   alembic downgrade -1
   # Result: Tables reverted to Integer primary keys without tool_calls fields
   ```

3. **Re-upgrade Test**: PASSED
   ```bash
   alembic upgrade head
   # Result: Successfully re-applied migration
   ```

4. **Schema Verification**: PASSED
   ```bash
   python verify_migration.py
   # Result: All 10 requirements verified
   ```

### Data Integrity

- No data loss during migration (expected, as tables were empty)
- All foreign key constraints properly recreated
- All indexes properly recreated
- All triggers properly recreated

---

## Deployment Notes

### Prerequisites

1. Backup production database before applying migration
2. Ensure `DATABASE_URL` environment variable is set
3. Alembic must be at revision `69ef5db393b3` before applying this migration

### Deployment Steps

**Local/Development**:
```bash
cd backend
alembic upgrade 003
```

**Production** (via kubectl):
```bash
# 1. Backup database first!
# 2. Apply migration
kubectl exec <backend-pod> -c backend -- alembic upgrade 003

# 3. Verify
kubectl exec <backend-pod> -c backend -- python verify_migration.py
```

### Rollback Plan

If issues occur:
```bash
# Downgrade to previous revision
alembic downgrade -1

# Or restore from backup
# (Follow Neon database restore procedure)
```

---

## Impact Assessment

### Breaking Changes

1. **Conversation IDs changed from Integer to UUID**
   - Frontend must handle UUID format
   - API responses will return UUID strings
   - Existing conversation references will be invalid

2. **Message IDs changed from Integer to UUID**
   - Frontend must handle UUID format
   - API responses will return UUID strings

3. **New required field: conversations.title**
   - All conversations now have a title (default: "New Conversation")
   - Frontend should display title in conversation list

4. **New role values: 'system' and 'tool'**
   - Frontend must handle these new message roles
   - Chat UI should handle tool messages appropriately

### Non-Breaking Additions

1. **tool_calls JSON field** (nullable)
   - Optional field for AI agent state
   - Frontend can ignore if not implementing AI features

2. **tool_call_id and name fields** (nullable)
   - Used internally by agent for tool execution
   - Frontend typically doesn't need to display these

---

## Post-Migration Tasks

- [ ] Update frontend TypeScript types to use UUID for conversation/message IDs
- [ ] Update API client to handle UUID format
- [ ] Update chat UI to display conversation titles
- [ ] Update chat UI to handle 'system' and 'tool' message roles
- [ ] Test conversation creation via API
- [ ] Test message sending via API
- [ ] Test conversation listing via API
- [ ] Verify AI agent can use tool_calls field
- [ ] Monitor database performance with new indexes

---

## Files Modified

1. `backend/app/models/conversation.py` - Updated Conversation model
2. `backend/app/models/message.py` - Updated Message model
3. `backend/alembic/versions/003_update_chat_schema_for_tool_calls.py` - New migration

## Files Created

1. `backend/check_tables.py` - Database inspection script
2. `backend/verify_migration.py` - Migration verification script
3. `MIGRATION_SUMMARY.md` - This document

---

## Next Steps

1. Proceed to **Task 3**: Implement FastMCP Server with Task Tools
2. Proceed to **Task 4**: Implement Stateless AgentRunner
3. Proceed to **Task 5**: Create Chat API Endpoints
4. Proceed to **Task 6**: Build Custom React Chat Widget

---

## References

- Phase III Implementation Plan: `specs/plans/phase3-implementation-plan.md`
- OpenAI Tool Calls Documentation: https://platform.openai.com/docs/guides/function-calling
- Alembic Documentation: https://alembic.sqlalchemy.org/

---

**Status**: COMPLETED

**Date**: 2025-12-20

**Database State**: Ready for Phase III AI Chatbot implementation
