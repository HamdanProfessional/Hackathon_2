---
name: dev-utilities
description: Enforce Conventional Commits by running git commit -m 'feat(scope): description' with types feat/fix/docs/refactor/test, fix CORS errors by removing credentials: 'include' from fetch() and adding JWT via headers: { Authorization: `Bearer ${token}` }, and synchronize FastAPI Pydantic schemas to TypeScript interfaces by converting UUID→string, datetime→string, Optional[T]→T | null in frontend/types/api.ts. Use when standardizing git workflow, resolving 'blocked by CORS policy' errors, or keeping frontend types aligned with backend models.
---

# Development Utilities Skill

Enforce Conventional Commits, fix CORS errors, and sync API schemas.

## Common Scenarios

### Scenario 1: Create Conventional Commit for New Feature
**User Request**: "Commit the new task feature"

**Commands**:
```bash
# Stage changes
git add backend/app/models/task.py backend/app/routers/task.py

# Commit with conventional format
git commit -m "feat(tasks): add CRUD endpoints for task management"

# Breaking change (use ! after scope)
git commit -m "feat(tasks)!: change task title to required field"

# Bug fix
git commit -m "fix(auth): resolve JWT expiration issue"

# Documentation
git commit -m "docs(readme): update deployment instructions"

# Refactor
git commit -m "refactor(tasks): extract validation to service layer"

# Tests
git commit -m "test(tasks): add integration tests for task API"
```

**Commit Format**: `<type>(<scope>): <description>`

**Valid Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore

**Example Error Messages**:
- `❌ "commit message rejected"` - Missing conventional commit format
- `❌ "type must be one of..."` - Invalid commit type used
- `❌ "description too long"` - Exceeds 72 character limit

### Scenario 2: Fix "blocked by CORS policy" Error
**Error Message in Browser Console**:
```
Access to fetch at 'http://localhost:8000/tasks' from origin 'http://localhost:3000'
has been blocked by CORS policy: Response to preflight request doesn't pass access
control check: No 'Access-Control-Allow-Origin' header is present
```

**Root Cause**: Frontend using `credentials: "include"` with wildcard origins

**Fix Commands**:
```bash
# 1. Check frontend code
grep -r "credentials.*include" frontend/src/

# 2. Remove credentials mode
# File: frontend/src/lib/api.ts
# BEFORE:
fetch(url, { credentials: "include", headers: {...} })

# AFTER:
const token = localStorage.getItem('token');
fetch(url, { headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}})

# 3. Verify backend CORS
# File: backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origins, not "*"
    allow_credentials=False,  # Must be False with specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"]
)
```

### Scenario 2: Fix "blocked by CORS policy" Error
**User Request**: "Frontend gets CORS error when calling backend"

**Actions**:
1. **Check frontend** - Look for `credentials: "include"` in fetch calls
2. **Remove credentials mode** - Delete `credentials: "include"` from fetch options
3. **Use JWT only** - Ensure token in `Authorization: Bearer <token>` header
4. **Check backend CORS** - Verify frontend URL in `allow_origins` list
5. **Verify no wildcard** - `allow_origins=["*"]` doesn't work with credentials

### Scenario 3: Sync Pydantic Schema to TypeScript Interface
**User Request**: "Keep frontend types in sync with backend models"

**Actions**:
1. **Read backend schema** - Open `backend/app/schemas/task.py`
2. **Convert types** - UUID → string, datetime → string, Optional → | null
3. **Create TS interface** - Create `frontend/types/task.ts`
4. **Map enums** - Convert Python Enum to TypeScript union type
5. **Validate sync** - Run schema validation script to check mismatches

### Scenario 4: Fix Git Commit Message Format
**User Request**: "Commit message rejected by hook"

**Actions**:
1. **Check format** - Must be `<type>(<scope>): <description>`
2. **Valid types** - feat, fix, docs, style, refactor, perf, test, build, ci, chore
3. **Scope** - Feature or module name (tasks, auth, database)
4. **Description** - Lowercase, no period, max 72 chars
5. **Fix example** - `Added login feature` → `feat(auth): add login endpoint`

---

## Quick Templates

### Conventional Commit Formats
```bash
# Feature
feat(tasks): add task CRUD endpoints
feat(auth)!: break change - remove session support

# Bug fix
fix(tasks): resolve user_id filtering bug
fix(database): fix migration rollback issue

# Documentation
docs(readme): update deployment instructions
docs(api): add authentication examples

# Refactor
refactor(tasks): extract validation to service layer
refactor(auth): consolidate JWT utilities

# Tests
test(tasks): add integration tests for task API
test(e2e): cover login → dashboard flow

# Chore
chore(deps): upgrade fastapi to 0.100.0
chore(docker): optimize multi-stage build
```

### CORS Fix Pattern
```typescript
// BEFORE - Causes CORS error
const response = await fetch('/api/tasks', {
  credentials: "include",  // ❌ Remove this
  headers: { "Content-Type": "application/json" }
});

// AFTER - Works correctly
const token = localStorage.getItem('token');
const response = await fetch('/api/tasks', {
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`  // ✅ Use JWT only
  }
});
```

### Schema Sync (Python → TypeScript)
```python
# backend/app/schemas/task.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class TaskResponse(BaseModel):
    id: int
    user_id: UUID          # → string in TS
    title: str
    description: Optional[str]  # → | null in TS
    status: str
    created_at: datetime   # → string in TS
```

```typescript
// frontend/types/task.ts
export interface Task {
  id: number;
  user_id: string;        // UUID converted to string
  title: string;
  description: string | null;  // Optional becomes | null
  status: string;
  created_at: string;     // datetime becomes ISO string
}
```

---

See `examples/commit-examples.md` for commit message examples.

### Quick Validation

```bash
python .claude/skills/dev-utilities/scripts/validate_commit.py "feat(auth): add OAuth2"
```

---

## Part 2: CORS Fixer

See `examples/cors-fixes.md` for complete CORS error solutions.

### Quick Fix

Remove `credentials: "include"` from frontend fetch calls and use JWT in Authorization header only.

---

## Part 3: API Schema Sync

See `examples/schema-sync-examples.md` for complete schema synchronization examples.

### Validation Script

```bash
python .claude/skills/dev-utilities/scripts/validate_schema.py \
  backend/app/schemas/task.py \
  frontend/lib/types.ts
```

---

## Quality Checklist

For git commits:
- [ ] Commit message follows Conventional Commits format
- [ ] Type is valid (feat, fix, docs, etc.)
- [ ] Description starts with lowercase, no period
- [ ] Header length under 72 characters
- [ ] Breaking changes use both `!` and footer
- [ ] Issue references included (if applicable)

For CORS:
- [ ] No CORS errors in browser console
- [ ] Backend CORS middleware configured
- [ ] Frontend removed credentials mode
- [ ] JWT in Authorization header only
- [ ] Environment-specific origins set
- [ ] Preflight OPTIONS requests succeed

For API sync:
- [ ] Backend Pydantic schemas defined
- [ ] Frontend TypeScript interfaces match
- [ ] Type conversions correct (UUID→string, datetime→string)
- [ ] Optional fields mapped to `| null`
- [ ] Enum types defined on both sides
- [ ] Validation tests pass
