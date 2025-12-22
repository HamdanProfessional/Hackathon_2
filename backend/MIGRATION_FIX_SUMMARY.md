# Database Schema Fix - User Password Fields

## Problem

The application was failing to create users with the following error:

```
null value in column "password_hash" of relation "users" violates not-null constraint
```

## Root Cause

1. **Schema Mismatch**: The database had `password_hash` column defined as `NOT NULL`, but the User model defined it as `nullable=True`
2. **Migration History Issue**: The production database was at revision `b162bbe44d72` which didn't exist in the codebase
3. **Duplicate Password Fields**: The User model had two password fields:
   - `hashed_password` (primary, NOT NULL)
   - `password_hash` (legacy, should be nullable)

## Solution Applied

### Step 1: Fixed Migration History
- Manually updated `alembic_version` table from invalid revision `b162bbe44d72` to `004`
- This aligned the database state with the current migration tree

### Step 2: Created New Migration
- Created migration `8ba965dfadfa`: "Make password_hash nullable to match model definition"
- Changed `password_hash` column from `NOT NULL` to `nullable=True`
- This aligns the database schema with the User model definition

### Step 3: Updated Model Documentation
- Added clear documentation to explain why both password fields exist
- Clarified that `hashed_password` is the primary field
- Documented that `password_hash` is legacy and can be NULL

## Files Modified

1. **Migration**: `alembic/versions/8ba965dfadfa_make_password_hash_nullable_to_match_.py`
   - Alters `users.password_hash` to be nullable

2. **Model**: `app/models/user.py`
   - Added comprehensive docstring explaining the two password fields
   - Clarified which field to use when creating users

3. **Database**: `alembic_version` table
   - Updated from invalid revision to current state

## Current State

- Users can now be created successfully by setting only `hashed_password`
- The `password_hash` field is optional (nullable)
- Both fields are kept for backward compatibility with any existing data
- The schema is now aligned between database and model

## Testing

User creation tested and verified working:
```python
user = User(
    email="test3@test.com",
    hashed_password="$2b$12$...",  # Only set this field
    name="testdeploy"
)
# password_hash is automatically NULL - this is OK
```

## Recommendations

For future cleanup:
1. Consider removing `password_hash` column entirely if not used
2. Or migrate all data to use only `hashed_password`
3. Keep only one password field for clarity

For now, the current solution maintains backward compatibility while fixing the immediate issue.
