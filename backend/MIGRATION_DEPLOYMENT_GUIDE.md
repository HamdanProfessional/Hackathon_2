# Database Migration Deployment Guide

## Recent Migrations

### Migration 004: Fix message_role ENUM to VARCHAR(20)

**Issue**: Production database has a `message_role` ENUM type, but SQLAlchemy model expects VARCHAR(20), causing:
```
column "role" is of type message_role but expression is of type character varying
```

**Solution**: Migration `004_fix_message_role_enum_to_varchar.py` safely converts ENUM to VARCHAR(20) with CHECK constraint.

See "Migration 004 Details" section below for full deployment instructions.

---

### Migration 5e990c3ddfe4: Add tool_call_id and name columns

**Issue**: Production database is missing `tool_call_id` and `name` columns in the `messages` table, causing:
```
column messages.tool_call_id does not exist
```

**Solution**: Migration `5e990c3ddfe4_add_missing_tool_columns_to_messages.py` safely adds these columns.

## Migration Details

### Revision ID
`5e990c3ddfe4`

### Revises
`001_fix_priority_schema`

### Files Modified
- `backend/alembic/versions/5e990c3ddfe4_add_missing_tool_columns_to_messages.py` (created)

### Columns Added
1. **tool_call_id**
   - Type: `String(100)`
   - Nullable: `True`
   - Purpose: Links tool role messages to assistant's tool_calls[].id

2. **name**
   - Type: `String(100)`
   - Nullable: `True`
   - Purpose: Function name for tool role messages

## Safety Features

This migration is **PRODUCTION-SAFE** because:

1. **Idempotent**: Uses `column_exists()` helper to check if columns exist before adding
2. **Non-destructive**: Only adds columns, doesn't modify or delete data
3. **Nullable columns**: Both columns are nullable, so existing rows remain valid
4. **No default values**: Won't trigger updates on existing rows
5. **Graceful handling**: Skips column creation if already exists (safe to re-run)

## Deployment Steps

### Step 1: Verify Current State

Check which migration is currently applied:
```bash
cd backend
alembic current
```

### Step 2: Backup Database (Recommended)

Before running any migration, backup your production database:
```bash
# For Neon Postgres, use Neon's backup feature or:
pg_dump $DATABASE_URL > backup_before_tool_columns_$(date +%Y%m%d_%H%M%S).sql
```

### Step 3: Test Migration (Optional - Staging)

If you have a staging environment, test there first:
```bash
cd backend
alembic upgrade 5e990c3ddfe4
```

Verify columns were added:
```sql
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns
WHERE table_name = 'messages'
  AND column_name IN ('tool_call_id', 'name');
```

Expected output:
```
 column_name  | data_type         | character_maximum_length | is_nullable
--------------+-------------------+--------------------------+-------------
 tool_call_id | character varying | 100                      | YES
 name         | character varying | 100                      | YES
```

### Step 4: Apply to Production

```bash
cd backend

# Set production DATABASE_URL if not already set
export DATABASE_URL="postgresql://user:pass@host/database?sslmode=require"

# Run migration
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade 001_fix_priority_schema -> 5e990c3ddfe4, add_missing_tool_columns_to_messages
Added column 'tool_call_id' to messages table
Added column 'name' to messages table
```

If columns already exist (migration already applied):
```
INFO  [alembic.runtime.migration] Running upgrade 001_fix_priority_schema -> 5e990c3ddfe4, add_missing_tool_columns_to_messages
Column 'tool_call_id' already exists in messages table - skipping
Column 'name' already exists in messages table - skipping
```

### Step 5: Verify Migration Success

```bash
# Check current revision
alembic current
```

Should show:
```
5e990c3ddfe4 (head)
```

Or run the verification script:
```bash
cd backend
python verify_migration.py
```

Look for:
```
[OK] Requirement 7: messages.tool_call_id is String(100, nullable)
[OK] Requirement 8: messages.name is String(100, nullable)
```

### Step 6: Restart Application

After migration, restart your backend application:
```bash
# If using systemd
sudo systemctl restart todo-backend

# If using Docker
docker-compose restart backend

# If using Kubernetes
kubectl rollout restart deployment/backend

# If running locally
# Stop the server (Ctrl+C) and restart:
uvicorn app.main:app --reload --port 8000
```

### Step 7: Test Chat Functionality

Test that the error is resolved:
```bash
# Make a chat request with tool calls
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "YOUR_CONVERSATION_ID",
    "message": "List my tasks"
  }'
```

Should return successfully without "column does not exist" error.

## Rollback (If Needed)

If you need to rollback:

```bash
cd backend
alembic downgrade 001_fix_priority_schema
```

This will remove the `tool_call_id` and `name` columns.

**WARNING**: Only rollback if you haven't sent any messages with tool calls. Rolling back will delete these columns and their data.

## Troubleshooting

### Issue: "Column already exists" error
**Solution**: This means the migration was partially applied. The migration is idempotent and will skip existing columns. Just re-run `alembic upgrade head`.

### Issue: "No such revision" error
**Solution**: Make sure you're in the `backend` directory and the migration file exists:
```bash
ls -la alembic/versions/5e990c3ddfe4_add_missing_tool_columns_to_messages.py
```

### Issue: Database connection error
**Solution**: Verify your `DATABASE_URL` environment variable is set correctly:
```bash
echo $DATABASE_URL
```

Should be in format:
```
postgresql://user:password@host:5432/database?sslmode=require
```

### Issue: Permission denied
**Solution**: Ensure the database user has `ALTER TABLE` permissions:
```sql
GRANT ALTER ON TABLE messages TO your_database_user;
```

## Migration History

After applying this migration, your history should look like:
```
000 -> 001 -> ... -> 001_fix_priority_schema -> 5e990c3ddfe4 (head)
```

## Data Integrity Verification

After migration, verify no data was lost:

```sql
-- Check total message count before and after
SELECT COUNT(*) FROM messages;

-- Verify all existing messages still have their data
SELECT id, conversation_id, role, content
FROM messages
LIMIT 5;

-- Check that new columns are added
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'messages'
ORDER BY ordinal_position;
```

## Post-Migration Checklist

- [ ] Migration applied successfully (`alembic current` shows `5e990c3ddfe4`)
- [ ] Both columns exist (`tool_call_id`, `name`)
- [ ] Both columns are `String(100)` and nullable
- [ ] Existing messages still have all their data
- [ ] Message count unchanged
- [ ] Backend application restarted
- [ ] Chat functionality working (no "column does not exist" error)
- [ ] Tool calls can be saved to database
- [ ] No errors in application logs

## Notes

- This migration is safe to run multiple times (idempotent)
- No data loss will occur (only adds columns)
- Existing rows will have `NULL` values for new columns
- New tool call messages will populate these columns
- Total downtime: < 1 second (adding nullable columns is fast)

## Support

If issues persist after migration:

1. Check application logs for specific errors
2. Verify database schema matches Message model
3. Ensure all pending migrations are applied
4. Test with a simple SELECT query to verify columns exist
5. Contact database administrator if permissions issues occur

---

---

# Migration 004 Details: Fix message_role ENUM to VARCHAR(20)

## Problem
Production database (Vercel/Neon) has a `message_role` ENUM type for the `messages.role` column, but the SQLAlchemy model expects VARCHAR(20). This causes insert failures with:

```
column "role" is of type message_role but expression is of type character varying
```

## Solution
Migration `004_fix_message_role_enum_to_varchar.py` safely converts the ENUM to VARCHAR(20) with a CHECK constraint.

## Migration Details

**File**: `backend/alembic/versions/004_fix_message_role_enum_to_varchar.py`
**Revision ID**: `004`
**Revises**: `5e990c3ddfe4`

**What it does**:
1. Detects if `message_role` ENUM type exists in the database
2. If it exists:
   - Converts `messages.role` column from ENUM to VARCHAR(20)
   - Drops the `message_role` ENUM type
   - Ensures CHECK constraint is in place: `role IN ('user', 'assistant', 'system', 'tool')`
3. If it doesn't exist (already VARCHAR):
   - Verifies CHECK constraint exists
   - No changes needed

**Idempotent**: Safe to run multiple times on both production and local databases.

---

## Deployment Instructions for Migration 004

### Prerequisites

1. **Backup Database** (CRITICAL):
   ```bash
   # For Neon/PostgreSQL production database
   # Use Neon dashboard or pg_dump to create a backup
   pg_dump $DATABASE_URL > backup_before_migration_004.sql
   ```

2. **Verify Current Schema** (Optional):
   ```sql
   -- Check if message_role ENUM exists
   SELECT typname FROM pg_type WHERE typname = 'message_role';

   -- Check current column type
   SELECT column_name, data_type
   FROM information_schema.columns
   WHERE table_name = 'messages' AND column_name = 'role';
   ```

### Deployment Steps

#### Option 1: Deploy via Vercel (Recommended)

1. **Commit Migration**:
   ```bash
   git add backend/alembic/versions/004_fix_message_role_enum_to_varchar.py
   git commit -m "fix(db): Convert message_role ENUM to VARCHAR(20)"
   git push origin main
   ```

2. **Run Migration on Production**:
   ```bash
   # SSH into production environment or use Vercel CLI
   cd backend
   alembic upgrade head
   ```

3. **Verify Migration**:
   ```bash
   # Check current revision
   alembic current
   # Should show: 004 (head)

   # Verify schema
   psql $DATABASE_URL -c "
     SELECT column_name, data_type
     FROM information_schema.columns
     WHERE table_name = 'messages' AND column_name = 'role';
   "
   # Should show: role | character varying
   ```

#### Option 2: Manual Migration (Direct Database Access)

If you have direct access to the production database:

1. **Connect to Production Database**:
   ```bash
   psql $DATABASE_URL
   ```

2. **Run Migration Manually**:
   ```sql
   -- Step 1: Check if ENUM exists
   SELECT typname FROM pg_type WHERE typname = 'message_role';

   -- Step 2: If ENUM exists, convert to VARCHAR
   ALTER TABLE messages
   ALTER COLUMN role TYPE VARCHAR(20)
   USING role::text;

   -- Step 3: Add CHECK constraint if it doesn't exist
   ALTER TABLE messages
   ADD CONSTRAINT check_role_values
   CHECK (role IN ('user', 'assistant', 'system', 'tool'));

   -- Step 4: Drop ENUM type
   DROP TYPE message_role;

   -- Step 5: Update alembic_version to mark migration as applied
   UPDATE alembic_version SET version_num = '004';
   ```

3. **Verify**:
   ```sql
   -- Check column type
   \d messages

   -- Should show:
   -- role | character varying(20) | not null
   -- Check constraints:
   --   "check_role_values" CHECK (role::text = ANY (ARRAY['user'::character varying, ...]))
   ```

---

## Testing (Migration 004)

### Local Testing (Already Completed)

The migration has been tested locally with the following scenarios:

1. ✅ **VARCHAR to VARCHAR** (idempotent):
   ```
   [INFO] No message_role ENUM detected - column is already VARCHAR(20)
   [INFO] CHECK constraint already exists
   [SUCCESS] Migration complete: Schema already correct
   ```

2. ✅ **ENUM to VARCHAR** (conversion):
   ```
   [INFO] Detected message_role ENUM type - converting to VARCHAR(20)
   [INFO] Converted messages.role from ENUM to VARCHAR(20)
   [INFO] Added CHECK constraint: check_role_values
   [INFO] Dropped message_role ENUM type
   [SUCCESS] Migration complete
   ```

3. ✅ **Downgrade** (rollback):
   ```
   [INFO] Created message_role ENUM type
   [INFO] Dropped CHECK constraint
   [INFO] Converted messages.role from VARCHAR(20) to message_role ENUM
   [SUCCESS] Downgrade complete
   ```

### Production Verification

After deploying to production:

1. **Test Insert**:
   ```python
   # Test that message inserts work correctly
   from app.models.message import Message

   message = Message(
       conversation_id="...",
       role="user",
       content="Test message"
   )
   # Should succeed without type errors
   ```

2. **Check Existing Data**:
   ```sql
   -- Verify no data was lost
   SELECT COUNT(*) FROM messages;

   -- Verify role values are intact
   SELECT role, COUNT(*) FROM messages GROUP BY role;
   ```

---

## Rollback Plan (Migration 004)

If the migration causes issues, you can rollback:

```bash
# Rollback to previous revision
cd backend
alembic downgrade -1

# Verify rollback
alembic current
# Should show: 5e990c3ddfe4 (head)
```

**WARNING**: Rollback will convert VARCHAR back to ENUM. This is safe but ensure the application is compatible.

---

## Post-Migration Checklist (Migration 004)

After successful migration:

- [ ] Verify `alembic current` shows revision `004`
- [ ] Test message insert via API endpoint
- [ ] Check application logs for any type errors
- [ ] Verify existing messages are still accessible
- [ ] Monitor production errors for 24 hours
- [ ] Remove backup file after 7 days (if no issues)

---

## Troubleshooting (Migration 004)

### Migration Fails with "ENUM does not exist"

**Cause**: Migration tried to drop ENUM that doesn't exist.

**Solution**: This shouldn't happen with the idempotent migration, but if it does:
```bash
# Skip to next revision
alembic stamp 004
```

### Migration Fails with "CHECK constraint already exists"

**Cause**: Constraint name collision.

**Solution**: Drop existing constraint manually:
```sql
ALTER TABLE messages DROP CONSTRAINT check_role_values;
-- Then re-run migration
alembic upgrade head
```

### Application Shows Type Errors After Migration

**Cause**: Application code or ORM cache not updated.

**Solution**:
```bash
# Restart application
vercel --prod
# Or for local development
uvicorn app.main:app --reload
```

---

## Summary

**Migration 004 Status**: ✅ Tested locally, ready for production deployment
**Risk Level**: Low (idempotent, non-destructive)
**Estimated Downtime**: None (migration runs in seconds)

**Migration Chain**:
```
... -> 5e990c3ddfe4 -> 004 (head)
```
