---
name: qa-tester
description: Comprehensive QA testing skill for E2E tests, integration tests, unit tests, console app testing, pytest, jest, and playwright. Covers backend (FastAPI), frontend (Next.js/React), and full-stack testing with coverage reporting, test fixtures, mocks, and best practices.
version: 2.0.0
category: testing
tags: [testing, qa, pytest, jest, playwright, unit-tests, integration-tests, e2e, test-coverage, tdd]
dependencies: [pytest, jest, playwright, pytest-cov, testing-library, rspec]
---

# QA Tester Skill

Comprehensive testing guidance for backend, frontend, and full-stack applications.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | Test templates for all types |
| Scripts | `scripts/` | Test automation |
| Templates | `references/templates.md` | Reusable templates |
| Links | `references/links.md` | External resources |

## When to Use This Skill

Use this skill when:
- User says "Write tests", "Create test suite", or "Run tests"
- Creating E2E tests for user workflows
- Building integration tests for API endpoints
- Writing unit tests for functions/components
- Testing console applications (CLI)
- Need to increase code coverage
- Implementing TDD (Test-Driven Development)
- Before production deployment

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Tests timeout | Database not cleaned up | Use fixtures with proper teardown |
| Flaky tests | Race conditions | Add explicit waits/fixtures |
| Coverage low | Missing edge cases | Add tests for error paths |

---

## Test Types

- **Unit Tests**: Test individual functions/methods in isolation
- **Integration Tests**: Test API endpoints with database
- **E2E Tests**: Test complete user flows (browser automation)
- **Contract Tests**: Validate API request/response schemas
- **Performance Tests**: Load testing and benchmarking

---

## Backend Tests (pytest)

**Unit test template**:
```python
def test_function():
    result = my_function(input)
    assert result == expected
```

**Integration test with fixtures**:
```python
@pytest.fixture
def db_session():
    # Setup test database
    yield session
    # Cleanup
```

---

## Frontend Tests (Jest)

**Component test**:
```typescript
test('renders button', () => {
  render(<Button />)
  expect(screen.getByRole('button')).toBeInTheDocument()
});
```

---

## E2E Tests (Playwright)

```typescript
test('complete workflow', async ({ page }) => {
  await page.goto('/')
  await page.click('text=Login')
  // ...
});
```

---

## Quality Checklist

- [ ] All new code has unit tests
- [ ] Critical paths have integration tests
- [ ] Main flows have E2E tests
- [ ] Coverage meets threshold (80%+)
- [ ] Tests pass in CI/CD
- [ ] Tests are fast (< 10s unit, < 60s integration)
- [ ] Test data isolated
- [ ] No flaky tests
- [ ] Error cases tested
