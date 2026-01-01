# Code Quality - Evolution of TODO Edition

This guide documents the actual code quality patterns and tools used in the Evolution of TODO project.

## Tools Used

### Backend (Python)

#### Ruff (Linter & Formatter)
```bash
# Install
pip install ruff

# Lint code
ruff check .

# Format code
ruff format .

# Watch mode
ruff check --watch .
```

**Configuration (pyproject.toml):**
```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.lint.isort]
known-first-party = ["app"]
```

#### MyPy (Type Checker)
```bash
# Install
pip install mypy

# Check types
mypy .

# Strict mode
mypy --strict app/
```

**Configuration (pyproject.toml):**
```toml
[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Gradually enable
plugins = ["pydantic.mypy"]
```

#### Pytest (Testing)
```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/test_tasks.py

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

**Configuration (pyproject.toml):**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

### Frontend (TypeScript)

#### ESLint
```bash
# Lint code
npm run lint

# Fix issues
npm run lint -- --fix
```

**Configuration (.eslintrc.json):**
```json
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

#### TypeScript Compiler
```bash
# Type check
npx tsc --noEmit

# Watch mode
npx tsc --watch
```

**Configuration (tsconfig.json):**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

## Code Review Checklist

### Backend
- [ ] Type hints added to all functions
- [ ] Docstrings follow Google style
- [ ] Async/await used correctly
- [ ] Database operations use AsyncSession
- [ ] User isolation enforced (user_id filtering)
- [ ] Error handling with custom exceptions
- [ ] Events published (fire-and-forget)
- [ ] Tests written for new functionality
- [ ] No hardcoded credentials
- [ ] SQLModel models match Pydantic schemas

### Frontend
- [ ] TypeScript types defined
- [ ] "use client" directive added for interactive components
- [ ] Server components used by default
- [ ] Props properly typed
- [ ] Error boundaries added
- [ ] Loading states handled
- [ ] Form validation included
- [ ] ARIA labels for accessibility
- [ ] Tailwind classes used (no inline styles)
- [ ] Responsive design (mobile-first)

### Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for API endpoints
- [ ] E2E tests for user flows
- [ ] Coverage above 70%
- [ ] Tests isolated (no dependencies)
- [ ] Mock data used appropriately

## Security Best Practices

### Backend
```python
# 1. Never log sensitive data
logger.info(f"User {user_id} logged in")  # ✅ Good
logger.info(f"User with token {token} logged in")  # ❌ Bad

# 2. Use environment variables for secrets
from app.config import settings
api_key = settings.GROQ_API_KEY  # ✅ Good
api_key = "gsk_abc123"  # ❌ Bad

# 3. Validate input
from pydantic import Field, validator
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)  # ✅ Good

# 4. User isolation in queries
query = select(Task).where(Task.user_id == user_id)  # ✅ Good
query = select(Task)  # ❌ Bad - returns all users' tasks

# 5. SQL injection prevention (use ORM)
task = await db.get(Task, task_id)  # ✅ Good
query = f"SELECT * FROM tasks WHERE id = {task_id}"  # ❌ Bad
```

### Frontend
```typescript
// 1. Never expose secrets
const apiKey = process.env.NEXT_PUBLIC_API_URL  // ✅ Good (public URL)
const apiKey = "sk-abc123"  // ❌ Bad

// 2. Sanitize user input
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userInput);  // ✅ Good

// 3. Use HTTPS for API calls
const response = await fetch('https://api.example.com');  // ✅ Good

// 4. Store tokens securely
localStorage.setItem('token', token);  // ✅ OK for JWT
document.cookie = `token=${token}; secure; httponly`;  // Better

// 5. Validate data from API
if (response.ok) {  // ✅ Good
  const data = await response.json();
}
```

## Performance Optimization

### Backend
```python
# 1. Use selectinload for relationships
from sqlalchemy.orm import selectinload
stmt = select(Task).options(selectinload(Task.priority_obj))  # ✅ Good

# 2. Pagination for list endpoints
query = query.limit(20).offset(0)  # ✅ Good
query = query.all()  # ❌ Bad - loads everything

# 3. Database indexes
class Task(SQLModel, table=True):
    user_id: str = Field(foreign_key="users.id", index=True)  # ✅ Good
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

# 4. Async operations
await db.commit()  # ✅ Good
db.commit()  # ❌ Bad - blocking

# 5. Background tasks for slow operations
background_tasks.add_task(send_email, user_email, data)  # ✅ Good
await send_email(user_email, data)  # ❌ Bad - blocks response
```

### Frontend
```typescript
// 1. Code splitting
const HeavyComponent = dynamic(() => import('./HeavyComponent'));  // ✅ Good

// 2. Image optimization
import Image from 'next/image';  // ✅ Good
<img src="/logo.png" />  // ❌ Bad

// 3. Memoization
import { useMemo } from 'react';
const expensiveValue = useMemo(() => computeExpensiveValue(data), [data]);  // ✅ Good

// 4. Debouncing
import { useDebounce } from '@/hooks/use-debounce';
const debouncedSearch = useDebounce(searchTerm, 300);  // ✅ Good

// 5. Virtual scrolling for long lists
import { useVirtualizer } from '@tanstack/react-virtual';  // ✅ Good
```

## Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run Ruff
echo "Running Ruff..."
ruff check .
if [ $? -ne 0 ]; then
    echo "Ruff check failed. Run 'ruff check .' and fix issues."
    exit 1
fi

# Run tests
echo "Running tests..."
pytest --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed. Fix them before committing."
    exit 1
fi

# TypeScript check
echo "TypeScript checking..."
cd frontend && npx tsc --noEmit
if [ $? -ne 0 ]; then
    echo "TypeScript check failed."
    exit 1
fi

echo "All checks passed!"
```

## CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      - name: Run Ruff
        run: ruff check .
      - name: Run tests
        run: pytest --cov=app --cov-report=xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: TypeScript check
        run: cd frontend && npx tsc --noEmit
      - name: Lint
        run: cd frontend && npm run lint
```

## Code Quality Commands Summary

```bash
# Backend
ruff check .          # Lint
ruff format .         # Format
mypy .                # Type check
pytest                # Test
pytest --cov          # Test with coverage

# Frontend
npm run lint          # Lint
npx tsc --noEmit      # Type check
npm test              # Test
npm run test:e2e      # E2E test

# Both
docker-compose build   # Build containers
docker-compose up -d   # Start services
```
