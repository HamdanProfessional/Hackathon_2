# Git Conventional Commits

Examples of proper commit message formats.

## Simple Commit

```
feat(auth): add OAuth2 support
```

## Bug Fix with Issue

```
fix(api): resolve null pointer exception

Fixes #123
```

## Breaking Change

```
feat(api)!: redesign user endpoints

BREAKING CHANGE: endpoints moved from /api/users to /api/v2/users
```

## Complex with Body

```
feat(tasks): add task filtering and search

Add comprehensive filtering by status, priority, and date range.
Implement full-text search across task titles and descriptions.

- Add query parameters to /tasks endpoint
- Implement database indexes for search performance
- Update frontend filter component

Closes #456
```

## Types Reference

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, semicolons)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding/updating tests
- `build`: Build system or dependencies
- `ci`: CI/CD changes
- `chore`: Maintenance
- `revert`: Revert previous commit
