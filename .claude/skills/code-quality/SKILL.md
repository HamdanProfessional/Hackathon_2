---
name: code-quality
description: Review Python code by running ruff check . for linting and mypy backend/ for type checking, scan for vulnerabilities with bandit -r backend/ and safety check, measure API response times with @timeit decorators or cProfile, analyze Next.js bundle sizes with npm run build --analyze, and enforce best practices via pre-commit hooks with .pre-commit-config.yaml. Use when validating code before PR merge, detecting SQL injection vulnerabilities, or optimizing database queries with EXPLAIN ANALYZE.
---

# Code Quality Skill

Review Python code with ruff/mypy, scan security with bandit, and analyze API performance.

## Common Scenarios

### Scenario 1: Review Python Code Before PR Merge
**User Request**: "Review this backend code before merging"

**Actions**:
1. **Run linter** - `ruff check backend/ --fix` for auto-fixable issues
2. **Type check** - `mypy backend/` to catch type errors
3. **Security scan** - `bandit -r backend/` for vulnerabilities
4. **Format check** - `ruff format --check backend/`
5. **Check issues**:
   - Missing type hints on function parameters
   - Unused imports or variables
   - Lines longer than 88 characters
   - Missing docstrings on public functions
6. **Report findings** - List issues with file:line locations

### Scenario 2: Detect SQL Injection Vulnerability
**User Request**: "Check for SQL injection risks"

**Actions**:
1. **Search for raw SQL** - `grep -r "execute(" backend/` for raw queries
2. **Check string interpolation**:
```python
# ❌ VULNERABLE - String interpolation
cursor.execute(f"SELECT * FROM tasks WHERE id = {task_id}")

# ✅ SAFE - Parameterized query
cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
```
3. **Verify ORM usage** - SQLModel/SQLAlchemy automatically prevents SQLi
4. **Check f-strings in queries** - Any query using f-string with user input is vulnerable
5. **Report findings** with safe alternatives

### Scenario 3: Find N+1 Query Performance Issue
**User Request**: "API is slow when listing tasks with comments"

**Actions**:
1. **Check query pattern**:
```python
# ❌ N+1 QUERY - Executes N+1 database calls
tasks = db.exec(select(Task)).all()
for task in tasks:
    comments = db.exec(select(Comment).where(Comment.task_id == task.id)).all()

# ✅ EAGER LOAD - Single query with join
from sqlalchemy.orm import selectinload
tasks = db.exec(
    select(Task)
    .options(selectinload(Task.comments))
).all()
```
2. **Add indexes** - Create index on foreign keys: `db.create_index("comments", ["task_id"])`
3. **Verify fix** - Check query count in logs

### Scenario 4: Analyze API Response Time Performance
**User Request**: "Measure API endpoint performance"

**Actions**:
1. **Add timing middleware** in `backend/app/main.py`:
```python
import time
@app.middleware("http")
async def add_timing(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Process-Time"] = str(duration)
    return response
```
2. **Test endpoints** - `curl -I http://localhost:8000/tasks` to see process time
3. **Identify slow endpoints** - Any > 200ms needs optimization
4. **Profile database** - Check query times with `EXPLAIN ANALYZE`
5. **Set targets** - P95 response time < 200ms

### Scenario 5: Check Hardcoded Secrets
**User Request**: "Scan for secrets in code"

**Actions**:
1. **Run bandit** - `bandit -r backend/ -f json` for security scan
2. **Check common patterns**:
   - `password = "..."` or `api_key = "..."`
   - `JWT_SECRET = "hardcoded"` in source files
   - Database URLs with credentials
3. **Verify environment usage**:
```python
# ❌ WRONG - Hardcoded secret
JWT_SECRET = "my-secret-key-min-32-chars"

# ✅ CORRECT - Environment variable
from pydantic import BaseSettings
class Settings(BaseSettings):
    JWT_SECRET: str
    class Config:
        env_file = ".env"
```
4. **Check .gitignore** - Ensure `.env` and `secrets/` excluded

---

## Quick Templates

### Pre-Merge Checklist (Python)
```bash
# Run all checks
ruff check backend/ --fix          # Lint and auto-fix
mypy backend/                     # Type checking
bandit -r backend/                # Security scan
pytest backend/tests/ --cov=app    # Tests with coverage
```

### Pre-Merge Checklist (TypeScript)
```bash
# Run all checks
npx eslint frontend/src/**/*.{ts,tsx} --fix
npx tsc --noEmit                   # Type checking
npm test                           # Jest tests
npm run lint                       # ESLint check
```

### Common Code Issues
| Issue | Detection | Fix |
|-------|-----------|-----|
| Missing type hints | mypy error | Add `param: Type` annotations |
| Line too long | ruff E501 | Break line or use black formatter |
| Unused import | ruff F401 | Remove unused import |
| SQL injection | bandit B608 | Use parameterized queries |
| Hardcoded secret | bandit B105 | Move to environment variable |
| N+1 query | Slow API logs | Add `selectinload()` eager load |

### Performance Targets
- API P95 response time: < 200ms
- Database query time: < 100ms
- Frontend bundle size: < 500KB (gzipped)
- Page load time: < 2 seconds
- Lighthouse score: > 90

---

**Backend Python**:
- [ ] Functions have type hints
- [ ] Docstrings present
- [ ] Variables are descriptive
- [ ] Functions focused (< 30 lines)
- [ ] No code duplication
- [ ] Proper use of constants
- [ ] Indexes created
- [ ] No raw SQL
- [ ] Proper HTTP status codes
- [ ] JWT authentication used
- [ ] Input validation
- [ ] Error handling

**Frontend TypeScript**:
- [ ] All variables typed
- [ ] No 'any' types
- [ ] Components functional
- [ ] Custom hooks extracted
- [ ] Props interfaces defined
- [ ] Components < 300 lines
- [ ] useCallback/useMemo used
- [ ] useEffect cleanup
- [ ] No state updates on unmounted
- [ ] Keys in lists
- [ ] Server Components by default
- [ ] Images use next/image

---

## Static Analysis Tools

**Python**:
```bash
ruff check backend/ --fix
mypy backend/
bandit -r backend/
safety check
pytest --cov=backend --cov-report=html
```

**TypeScript**:
```bash
npx eslint frontend/src/**/*.{ts,tsx} --fix
npx tsc --noEmit
npx prettier --write frontend/src/**/*.{ts,tsx}
```

---

## Performance Targets

- API response time: P95 < 200ms
- Database query time: < 100ms
- Frontend bundle size: < 500KB initial
- Page load time: < 2s
- Lighthouse score: > 90

---

## Quality Checklist

Before approving PR:
- [ ] All automated checks pass
- [ ] No critical security issues
- [ ] Code coverage >= 80%
- [ ] No obvious performance problems
- [ ] Code follows project conventions
- [ ] New features have tests
- [ ] Documentation updated
- [ ] Error handling comprehensive
- [ ] Resource cleanup proper
