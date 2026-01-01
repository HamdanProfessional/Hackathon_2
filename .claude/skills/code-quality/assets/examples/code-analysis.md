# Python Code Analysis Example

## Using Ruff (Fast Linter)

```bash
# Install ruff
pip install ruff

# Check code
ruff check .

# Fix issues
ruff check --fix .

# Format code
ruff format .
```

## Using Pylint

```bash
# Install pylint
pip install pylint

# Analyze code
pylint app/
```

## Coverage Report

```python
# tests/test_app.py
import pytest

def test_function():
    assert True

# Run with coverage
pytest --cov=app --cov-report=html
```

## Security Scan with Bandit

```bash
pip install bandit
bandit -r app/
```
