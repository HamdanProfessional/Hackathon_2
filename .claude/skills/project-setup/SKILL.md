---
name: project-setup
description: Initialize monorepo structure with mkdir -p backend frontend && touch pyproject.toml package.json, scaffold Python 3.13+ via uv init --package backend && uv add fastapi sqlmodel uvicorn, create Next.js apps via npx create-next-app@latest --typescript --tailwind, and set up Phase I CLI apps via Typer with @app.command() and Rich for tables/progress bars. Use when starting new projects with .gitignore (node_modules/__pycache__/.env), configuring development environments with virtualenvs, or scaffolding workspace management.
---

# Project Setup Skill

Complete project initialization and scaffolding.

## Quick Commands

```bash
# Initialize monorepo
mkdir -p backend frontend tests
cd .

# Setup Python backend with uv
cd backend
uv init --package backend
uv add fastapi sqlmodel uvicorn alembic

# Setup Next.js frontend
cd ../frontend
npx create-next-app@latest . --typescript --tailwind --app-dir --no-src-dir --import-alias "@/*"
npm install @types/node

# Setup Git
cd ..
git init
echo "node_modules
__pycache__
*.pyc
.env
.venv
dist
build" > .gitignore

# Initial commit
git add .
git commit -m "chore: initialize project structure"
```

## File Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry
│   │   ├── models/          # SQLModel tables
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API routes
│   │   └── config.py        # Settings
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend tests
│   └── pyproject.toml       # Python dependencies
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/          # React components
│   ├── lib/                 # Utilities
│   ├── package.json         # Node dependencies
│   └── next.config.js       # Next.js config
├── tests/                   # E2E tests
├── .gitignore
└── README.md
```

## Backend Setup (Python 3.13+)

```bash
# Create backend
mkdir backend
cd backend

# Initialize with uv
uv init --package backend

# Add dependencies
uv add fastapi sqlmodel uvicorn[standard] alembic psycopg2-binary pydantic
uv add --dev pytest pytest-cov ruff mypy

# Create app structure
mkdir -p app/models app/schemas app/routers

# Initialize Alembic
alembic init alembic

# Update alembic.ini
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

**File: `backend/app/main.py`**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Frontend Setup (Next.js 16+)

```bash
cd frontend

# Create Next.js app
npx create-next-app@latest . --typescript --tailwind --app-dir --no-src-dir

# Install additional dependencies
npm install axios

# Run dev server
npm run dev
```

**File: `frontend/app/page.tsx`**
```typescript
export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-3xl font-bold">Welcome</h1>
    </main>
  );
}
```

## Phase I CLI Setup (Typer)

```bash
# Create CLI app
mkdir cli
cd cli
uv init

# Add dependencies
uv add typer[all] rich

# Create CLI file
touch cli.py
```

**File: `cli/cli.py`**
```python
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def hello(name: str = typer.Argument(...)):
    """Say hello to someone."""
    console.print(f"[bold green]Hello, {name}![/bold green]")

if __name__ == "__main__":
    app()
```

**Run CLI**:
```bash
python cli/cli.py hello World
```
