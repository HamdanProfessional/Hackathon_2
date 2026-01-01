# Code Review Checklist

## Security
- [ ] No hardcoded credentials or API keys
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (input sanitization, output encoding)
- [ ] Authentication/authorization checks on sensitive endpoints
- [ ] Rate limiting on public APIs

## Performance
- [ ] No N+1 queries (use eager loading)
- [ ] Database indexes on frequently queried fields
- [ ] Pagination for list endpoints
- [ ] Caching for expensive operations
- [ ] Lazy loading where appropriate

## Error Handling
- [ ] Specific exception types (not bare except)
- [ ] Proper error messages (don't expose internals)
- [ ] Logging of errors with context
- [ ] Graceful degradation
- [ ] User-friendly error messages

## Code Quality
- [ ] Functions follow SRP (Single Responsibility Principle)
- [ ] DRY (Don't Repeat Yourself) - no duplicated code
- [ ] Meaningful variable/function names
- [ ] Type hints on all functions
- [ ] Docstrings on public functions
- [ ] Maximum function length (~50 lines)
- [ ] Maximum cyclomatic complexity (~10)

## Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for API endpoints
- [ ] Edge cases covered
- [ ] Mocking external dependencies
- [ ] Test coverage >80%

## Maintainability
- [ ] Consistent code style
- [ ] No commented-out code
- [ ] No unused imports or variables
- [ ] Dependencies up to date
- [ ] Documentation for complex logic
