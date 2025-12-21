# CRITICAL PRODUCTION FIX - UUID Schema Migration

## Problem
Production database has INTEGER columns for `conversations` and `messages` tables, but the code expects UUID columns. This is causing all conversation creation to fail with:
```
DatatypeMismatchError: column "id" is of type integer but expression is of type uuid
```

## Solution
We have created an emergency fix that will:

1. Drop the existing `conversations` and `messages` tables (if they exist)
2. Recreate them with proper UUID columns
3. Update the Alembic migration version
4. Verify the fix works

## How to Apply the Fix

### Option 1: Using the API Endpoint (Quick Fix)

1. Deploy the updated backend code (with the new `/force-migration` endpoint)
2. Make a POST request to the endpoint:
   ```bash
   curl -X POST https://your-production-api.com/force-migration
   ```
3. Verify the fix with:
   ```bash
   curl -X POST https://your-production-api.com/check-conversation-schema
   ```

### Option 2: Running the Script Directly (Recommended)

1. SSH into your production server
2. Navigate to the backend directory:
   ```bash
   cd /path/to/backend
   ```
3. Ensure the DATABASE_URL environment variable is set
4. Run the fix script:
   ```bash
   python fix_production_migration.py
   ```
5. The script will:
   - Check the current schema
   - Ask for confirmation
   - Apply the migration
   - Verify it worked

### Option 3: Manual SQL (Last Resort)

If automated methods fail, run these SQL commands directly:

```sql
-- Drop existing tables
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;

-- Recreate conversations with UUID columns
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX idx_conversations_created_at_desc
ON conversations (created_at DESC);

-- Recreate messages with UUID columns
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    tool_call_id VARCHAR(100),
    name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX idx_messages_conversation_created
ON messages (conversation_id, created_at);

-- Update alembic version
UPDATE alembic_version SET version_num = 'e940f362bb65';
```

## Verification

After applying the fix, verify it worked:

1. Check the schema:
   ```sql
   SELECT column_name, data_type
   FROM information_schema.columns
   WHERE table_name = 'conversations';
   ```

2. Test creating a conversation through the API or UI

3. Check logs for any remaining errors

## Data Loss Warning

⚠️ **IMPORTANT**: This fix will DROP and RECREATE the tables, which means:
- Any existing conversations will be lost
- Any existing messages will be lost

However, given that conversations are currently failing to create, it's likely these tables are empty or contain very little data.

## Root Cause Analysis

The automatic migration runner in `app/main.py` was configured to catch exceptions and only log a warning:
```python
try:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations complete")
except Exception as e:
    logger.warning(f"Database migration failed, but continuing: {e}")
```

This caused the migration to fail silently in production, leaving the database out of sync with the code.

## Prevention

To prevent this in the future:

1. Change the migration runner to fail loudly in production
2. Add health checks that verify database schema
3. Run migrations as a separate step before deploying code
4. Add monitoring for migration failures

## Testing After Fix

1. Try to create a new conversation in the UI
2. Send a message to the AI assistant
3. Verify the conversation persists after refresh
4. Check that no more UUID type errors appear in logs