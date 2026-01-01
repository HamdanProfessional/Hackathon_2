# Code Quality Tools

## Python

### Linters
- **Ruff** - Fast Python linter (recommended)
- **Pylint** - Comprehensive analysis
- **Flake8** - Style guide enforcement

### Type Checkers
- **mypy** - Static type checking
- **pyright** - Microsoft's type checker

### Security
- **bandit** - Security vulnerability scanner
- **safety** - Dependency vulnerability checker

### Coverage
- **pytest-cov** - Coverage plugin for pytest
- **coverage.py** - Code coverage measurement

## TypeScript/JavaScript

### Linters
- **ESLint** - JavaScript/TypeScript linter
- **TSLint** (deprecated, use ESLint)

### Type Checkers
- **tsc** - TypeScript compiler
- **ESLint with @typescript-eslint**

### Formatters
- **Prettier** - Code formatter
- **ESLint --fix** - Auto-fix issues

## Security Scanners
- **Snyk** - Dependency vulnerabilities
- **npm audit** - Node.js security audit
- **OWASP Dependency-Check** - Universal dependency scanner

## CI/CD Integration

### GitHub Actions
```yaml
- name: Lint with Ruff
  run: |
    pip install ruff
    ruff check .

- name: Type check
  run: |
    pip install mypy
    mypy app/

- name: Security scan
  run: |
    pip install bandit
    bandit -r app/
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format
```
