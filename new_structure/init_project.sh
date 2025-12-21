#!/bin/bash

# =============================================================================
# Todo Evolution Project Initialization Script
# =============================================================================
# This script sets up the complete project structure and dependencies
# Usage: ./init_project.sh [--phase <number>] [--skip-git]
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project information
PROJECT_NAME="Todo Evolution"
PROJECT_ROOT="$(pwd)"
PHASE=${2:-1}  # Default to Phase I
SKIP_GIT=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --phase)
            PHASE="$2"
            shift 2
            ;;
        --skip-git)
            SKIP_GIT=true
            shift
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_phase() {
    echo -e "${PURPLE}[PHASE ${PHASE}]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# =============================================================================
# INTRO
# =============================================================================
print_status "🚀 Initializing $PROJECT_NAME Project"
print_status "📍 Project Root: $PROJECT_ROOT"
print_phase "Setting up for Phase $PHASE development"

# =============================================================================
# VALIDATE PREREQUISITES
# =============================================================================
print_step "Validating prerequisites..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_status "✓ Python version: $PYTHON_VERSION"

# Check for UV
if ! command -v uv &> /dev/null; then
    print_warning "UV is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    print_status "✓ UV package manager found"
fi

# Check for Node.js (Phase II+)
if [ "$PHASE" -ge 2 ]; then
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required for Phase II+ but not installed."
        exit 1
    fi
    NODE_VERSION=$(node --version)
    print_status "✓ Node.js version: $NODE_VERSION"

    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed."
        exit 1
    fi
    print_status "✓ npm found"
fi

# =============================================================================
# GIT INITIALIZATION
# =============================================================================
if [ "$SKIP_GIT" = false ]; then
    print_step "Initializing Git repository..."

    if [ ! -d ".git" ]; then
        git init
        print_status "✓ Git repository initialized"

        # Create initial commit
        git add .env.example .gitignore USER_GUIDE.md CLAUDE.md requirements.md

        if [ -f "README.md" ]; then
            git add README.md
        fi

        git commit -m "Initial commit: Todo Evolution project setup

        🚀 Features:
        - Multi-phase architecture (I-V)
        - Spec-driven development workflow
        - AI-powered task management (Phase III)
        - Kubernetes deployment (Phase IV)
        - Event-driven microservices (Phase V)

        🛠️ Technologies:
        - Python 3.13+ with UV package manager
        - FastAPI + SQLModel backend
        - Next.js 16 + TypeScript frontend
        - Google Gemini 2.5 Flash AI integration
        - PostgreSQL with Neon DB
        - Docker + Kubernetes deployment

        📋 Phase Status: Phase $PHASE initialization complete

        🤖 Generated with Claude Code
        Co-Authored-By: Claude <noreply@anthropic.com>"

        print_status "✓ Initial commit created"
    else
        print_warning "Git repository already exists, skipping initialization"
    fi
else
    print_warning "Skipping Git initialization as requested"
fi

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================
print_step "Setting up environment configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "✓ Created .env from .env.example"
        print_warning "⚠️  Please edit .env with your actual API keys before continuing"
        print_warning "   Required: GOOGLE_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET"
    else
        print_error ".env.example not found. Cannot create .env file."
        exit 1
    fi
else
    print_warning ".env file already exists, skipping creation"
fi

# =============================================================================
# PROJECT STRUCTURE CREATION
# =============================================================================
print_step "Creating project structure..."

# Create core directories
directories=(
    ".specify/memory"
    ".specify/plans"
    ".specify/tasks"
    ".specify/architecture"
    ".specify/scripts"
    ".claude/agents"
    ".claude/skills"
    "specs/features"
    "specs/api"
    "specs/database"
    "specs/architecture"
    "logs"
    "tests"
    "docs"
)

# Phase-specific directories
if [ "$PHASE" -ge 1 ]; then
    directories+=("src")
fi

if [ "$PHASE" -ge 2 ]; then
    directories+=("backend" "frontend")
fi

if [ "$PHASE" -ge 4 ]; then
    directories+=("k8s")
fi

# Create directories
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_status "✓ Created directory: $dir"
    else
        print_warning "Directory already exists: $dir"
    fi
done

# =============================================================================
# PYTHON DEPENDENCIES SETUP
# =============================================================================
print_step "Setting up Python dependencies with UV..."

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    cat > pyproject.toml << 'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "todo-evolution"
version = "0.1.0"
description = "Evolution of Todo from console to cloud-native AI application"
authors = [{name = "Todo Evolution Team"}]
license = {text = "MIT"}
requires-python = ">=3.13"
dependencies = [
    # Core dependencies
    "rich>=13.0.0",
    "click>=8.0.0",
    "typer>=0.9.0",

    # Phase II+ dependencies
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlmodel>=0.0.14",
    "alembic>=1.12.0",
    "psycopg2-binary>=2.9.0",
    "better-auth>=0.8.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",

    # Phase III AI dependencies
    "openai>=1.3.0",
    "agents>=0.0.1",
    "ai-sdk>=0.0.1",

    # Development dependencies
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pre-commit>=3.5.0",
]

[project.scripts]
dev = "uvicorn main:app --reload"
test = "pytest"
test-cov = "pytest --cov=app tests/"
lint = "ruff check ."
format = "black ."
type-check = "mypy ."
EOF
    print_status "✓ Created pyproject.toml"
else
    print_warning "pyproject.toml already exists"
fi

# Sync dependencies
uv sync
print_status "✓ Python dependencies installed"

# =============================================================================
# NODE.JS SETUP (Phase II+)
# =============================================================================
if [ "$PHASE" -ge 2 ]; then
    print_step "Setting up Node.js dependencies..."

    # Create package.json if it doesn't exist
    if [ ! -f "package.json" ]; then
        cat > package.json << 'EOF'
{
  "name": "todo-evolution-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "16.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "tailwindcss": "^3.0.0",
    "autoprefixer": "^10.0.0",
    "postcss": "^8.0.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "class-variance-authority": "^0.7.0",
    "lucide-react": "^0.292.0",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "ai": "^3.0.0",
    "openai": "^4.0.0",
    "better-auth-react": "^0.8.0",
    "next-intl": "^3.0.0"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "eslint-config-next": "14.0.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
EOF
        print_status "✓ Created package.json"
    else
        print_warning "package.json already exists"
    fi

    # Install dependencies
    npm install
    print_status "✓ Node.js dependencies installed"
fi

# =============================================================================
# PHASE-SPECIFIC SETUP
# =============================================================================
case $PHASE in
    1)
        print_phase "Setting up Phase I: Console Application"

        # Create basic console app structure
        if [ ! -f "src/main.py" ]; then
            cat > src/main.py << 'EOF'
#!/usr/bin/env python3
"""
Todo Evolution - Phase I: Console Application
A simple command-line task manager with Rich UI.
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from typing import List, Optional
import json
import os
from datetime import datetime

app = typer.Typer(help="Todo Evolution - Console Task Manager")
console = Console()

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1
        self.data_file = "tasks.json"
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self.next_id = data.get('next_id', 1)
            except Exception:
                console.print("[yellow]Warning: Could not load tasks file[/yellow]")

    def save_tasks(self):
        """Save tasks to JSON file."""
        data = {
            'tasks': self.tasks,
            'next_id': self.next_id
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

@app.command()
def list():
    """List all tasks."""
    manager = TaskManager()

    if not manager.tasks:
        console.print("[yellow]No tasks found. Create one with 'add' command.[/yellow]")
        return

    table = Table(title="📋 Your Tasks")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Created", style="blue")

    for task in manager.tasks:
        status = "✅" if task['completed'] else "⏳"
        table.add_row(str(task['id']), task['title'], status, task['created_at'])

    console.print(table)

@app.command()
def add(
    title: str = typer.Argument(..., help="Task title"),
    description: Optional[str] = typer.Option(None, help="Task description")
):
    """Add a new task."""
    manager = TaskManager()

    task = {
        'id': manager.next_id,
        'title': title,
        'description': description or "",
        'completed': False,
        'created_at': datetime.now().isoformat()
    }

    manager.tasks.append(task)
    manager.next_id += 1
    manager.save_tasks()

    console.print(f"[green]✓ Task added: {title}[/green]")

@app.command()
def complete(task_id: int = typer.Argument(..., help="Task ID to complete")):
    """Mark a task as completed."""
    manager = TaskManager()

    for task in manager.tasks:
        if task['id'] == task_id:
            task['completed'] = True
            manager.save_tasks()
            console.print(f"[green]✓ Task {task_id} marked as complete[/green]")
            return

    console.print(f"[red]❌ Task {task_id} not found[/red]")

@app.command()
def delete(task_id: int = typer.Argument(..., help="Task ID to delete")):
    """Delete a task."""
    manager = TaskManager()

    original_count = len(manager.tasks)
    manager.tasks = [task for task in manager.tasks if task['id'] != task_id]

    if len(manager.tasks) < original_count:
        manager.save_tasks()
        console.print(f"[green]✓ Task {task_id} deleted[/green]")
    else:
        console.print(f"[red]❌ Task {task_id} not found[/red]")

@app.command()
def clear():
    """Clear all tasks."""
    if Confirm.ask("Are you sure you want to clear all tasks?"):
        manager = TaskManager()
        manager.tasks = []
        manager.next_id = 1
        manager.save_tasks()
        console.print("[green]✓ All tasks cleared[/green]")

if __name__ == "__main__":
    app()
EOF
            print_status "✓ Created Phase I console application"
        fi
        ;;
    2)
        print_phase "Setting up Phase II: Full Stack Web Application"

        # Create basic FastAPI structure
        if [ ! -f "backend/main.py" ]; then
            mkdir -p backend/app/{api,models,schemas,core}

            cat > backend/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

app = FastAPI(
    title="Todo Evolution API",
    description="RESTful API for task management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Todo Evolution API - Phase II"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "phase": "II"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
            print_status "✓ Created Phase II FastAPI backend structure"
        fi

        # Create basic Next.js structure
        if [ ! -f "frontend/package.json" ]; then
            mkdir -p frontend/{app,components,lib,styles}

            # Create next.config.js
            cat > frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig
EOF

            # Create tailwind.config.js
            cat > frontend/tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

            # Create postcss.config.js
            cat > frontend/postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

            print_status "✓ Created Phase II Next.js frontend structure"
        fi
        ;;
    3)
        print_phase "Setting up Phase III: AI Chatbot Integration"

        # Create AI directory structure
        mkdir -p backend/app/{ai,services}

        if [ ! -f "backend/app/ai/chat.py" ]; then
            cat > backend/app/ai/chat.py << 'EOF'
"""
AI Chat Integration for Todo Evolution - Phase III
Google Gemini 2.5 Flash with OpenAI Agents SDK
"""

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_default_openai_client
import os

# ⚠️ MANDATORY: Google Gemini 2.5 Flash configuration
class GeminiConfig:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        self.model = "gemini-2.0-flash-exp"

# Initialize Gemini configuration
gemini_config = GeminiConfig()
client = AsyncOpenAI(
    api_key=gemini_config.api_key,
    base_url=gemini_config.base_url
)
set_default_openai_client(client)
EOF
            print_status "✓ Created Phase III AI integration structure"
        fi
        ;;
esac

# =============================================================================
# FINAL SETUP
# =============================================================================
print_step "Finalizing setup..."

# Create .gitattributes for better file handling
cat > .gitattributes << 'EOF'
# Normalize line endings
* text=auto eol=lf

# Explicitly declare text files
*.md text
*.py text
*.js text
*.json text
*.yml text
*.yaml text

# Declare binary files
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.pdf binary
EOF

# Create pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.3
    hooks:
      - id: ruff
      - id: ruff-format
EOF

# Create README if it doesn't exist
if [ ! -f "README.md" ]; then
    cat > README.md << 'EOF
# 🚀 Todo Evolution

## Project Overview

A comprehensive 5-phase evolution project that transforms a simple Todo console application into a sophisticated cloud-native AI-powered task management system.

## Phases

- **Phase I**: Console Application (Python + Rich UI)
- **Phase II**: Full Stack Web Application (Next.js + FastAPI)
- **Phase III**: AI Chatbot Interface (Google Gemini + ChatKit)
- **Phase IV**: Kubernetes Deployment (Docker + K8s)
- **Phase V**: Cloud Native Event-Driven (Dapr + Kafka)

## Quick Start

1. Copy environment variables:
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your API keys
   \`\`\`

2. Install dependencies:
   \`\`\`bash
   uv sync
   npm install  # Phase II+
   \`\`\`

3. Run Phase I:
   \`\`\`bash
   uv run src/main.py
   \`\`\`

4. Run Phase II+:
   \`\`\`bash
   # Backend
   cd backend && uvicorn main:app --reload

   # Frontend
   cd frontend && npm run dev
   \`\`\`

## Architecture

- **Spec-Driven Development**: All features start with specifications
- **Agent-Based Development**: 40 specialized agents for different tasks
- **8 Core Skills**: Foundational capabilities for all agents
- **Phase Evolution**: Seamless transitions between development phases

## Documentation

- [USER_GUIDE.md](./USER_GUIDE.md) - Comprehensive user guide
- [CLAUDE.md](./CLAUDE.md) - Claude Code instructions
- [specs/](./specs/) - Feature specifications
- [requirements.md](./requirements.md) - Master requirements

## Getting Help

Use the agent system for development tasks:

\`\`\`bash
# Plan a new feature
@.claude/agents/architect.md Plan user authentication

# Implement backend
@.claude/agents/backend-specialist.md Create user API endpoints

# Create frontend
@.claude/agents/frontend-specialist.md Build login page
\`\`\`
EOF
    print_status "✓ Created README.md"
fi

# =============================================================================
# SUCCESS MESSAGE
# =============================================================================
echo
print_status "🎉 $PROJECT_NAME initialization complete!"
echo
print_phase "Phase $PHASE setup complete"
echo
print_status "📁 Project structure created"
print_status "🔧 Dependencies installed"
print_status "⚙️  Environment configured"
print_status "📚 Documentation ready"
echo
print_status "🚀 Next steps:"
echo "   1. Edit .env with your API keys (GOOGLE_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET)"
echo "   2. Run 'uv run src/main.py' for Phase I"
if [ "$PHASE" -ge 2 ]; then
    echo "   3. Run 'cd backend && uvicorn main:app --reload' for backend"
    echo "   4. Run 'cd frontend && npm run dev' for frontend"
fi
echo "   5. Check USER_GUIDE.md for detailed commands"
echo
print_status "📖 For detailed instructions, see: USER_GUIDE.md"
print_status "🤖 For agent help, check: CLAUDE.md"

exit 0