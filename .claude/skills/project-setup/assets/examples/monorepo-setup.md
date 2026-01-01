# Project Setup Example

## Monorepo Structure

```
todo-app/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── api/                 # FastAPI backend
├── packages/
│   ├── ui/                  # Shared UI components
│   ├── types/               # Shared TypeScript types
│   └── config/              # Shared configuration
├── package.json
├── pnpm-workspace.yaml
└── turbo.json
```

## pnpm-workspace.yaml

```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

## package.json

```json
{
  "name": "todo-app-monorepo",
  "private": true,
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test"
  },
  "devDependencies": {
    "turbo": "^1.10.0"
  },
  "workspaces": [
    "apps/*",
    "packages/*"
  ]
}
```

## Python UV Setup

```bash
# Install uv
pip install uv

# Create project
uv init --name todo-app

# Add dependencies
uv add fastapi uvicorn sqlmodel
uv add --dev pytest ruff mypy

# Run development server
uv run uvicorn app.main:app --reload
```

## pyproject.toml

```toml
[project]
name = "todo-app"
version = "0.1.0"
description = "Todo application"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlmodel>=0.0.14",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```
