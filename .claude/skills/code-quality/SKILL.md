---
name: code-quality
description: Comprehensive code quality analysis including code review (security, performance, testing, best practices), performance analysis (API response times, database queries, frontend rendering, bundle sizes), and actionable feedback for Python, TypeScript, and SQL code.
version: 2.0.0
category: quality
tags: [code-review, quality, security, performance, best-practices, static-analysis, linting, optimization]
dependencies: [ruff, mypy, eslint, prettier, bandit, safety, lighthouse]
---

# Code Quality Skill

Comprehensive code review, performance analysis, and quality assurance.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | Code review patterns |
| Scripts | `scripts/` | Quality validation |
| Templates | `references/templates.md` | Reusable templates |
| Links | `references/links.md` | External resources |

## When to Use This Skill

Use this skill when:
- User says "Review this code" or "Check code quality"
- Pull request needs review before merging
- Want to ensure code follows best practices
- Need security vulnerability scan
- Checking performance bottlenecks
- Validating test coverage
- Before production deployment

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| N+1 queries | Missing eager loading | Use `selectinload()` |
| SQL injection risk | Raw SQL with interpolation | Use parameterized queries |
| Hardcoded secrets | Secrets in code | Move to environment variables |
| Missing types | No type hints | Add proper annotations |
| Slow API | Unoptimized queries | Add indexes, limit results |

---

## Code Review Checklist

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
