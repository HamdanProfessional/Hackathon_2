# CLI Builder - Evolution of TODO Edition

## Phase I: Console App CLI

The Evolution of TODO project started as a monolithic CLI application in Phase I. While the project has evolved to use FastAPI and Next.js, the CLI patterns are still useful for scripts and utilities.

## Current CLI Usage in the Project

### 1. Alembic Migration CLI

```bash
# Create a new migration
alembic revision --autogenerate -m "Add user preferences table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### 2. UV Package Manager (Python 3.13+)

```bash
# Install UV
pip install uv

# Create new project
uv init --name todo-app

# Add dependencies
uv add fastapi uvicorn sqlmodel

# Add dev dependencies
uv add --dev pytest ruff mypy

# Run scripts
uv run python scripts/generate_gmail_token.py

# Run development server
uv run uvicorn app.main:app --reload
```

### 3. Docker/Compose CLI

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild specific service
docker-compose up -d --build backend

# Execute command in container
docker-compose exec backend python -m pytest
```

### 4. Kubernetes CLI (kubectl)

```bash
# Apply all manifests
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/

# Get pod status
kubectl get pods -w

# View logs
kubectl logs -f deployment/todo-backend

# Port forward to local
kubectl port-forward deployment/todo-backend 8000:8000

# Describe pod for debugging
kubectl describe pod todo-backend-xxxxx
```

### 5. Helm CLI

```bash
# Install chart
helm install todo-app ./helm/todo-app

# Upgrade chart
helm upgrade todo-app ./helm/todo-app

# Uninstall chart
helm uninstall todo-app

# List releases
helm list

# Get values
helm get values todo-app
```

### 6. npm/yarn CLI (Frontend)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production server
npm start

# Run tests
npm test

# Add shadcn/ui component
npx shadcn-ui@latest add button
```

## Creating Custom Scripts

### Python Script Example

```python
#!/usr/bin/env python3
"""
Generate Gmail OAuth token for email notifications.
"""
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def generate_gmail_token():
    """Generate and save Gmail OAuth token."""
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    # Load client secrets
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        SCOPES
    )

    # Run OAuth flow
    credentials = flow.run_local_server(port=0)

    # Save credentials
    with open('gmail_token.json', 'w') as token_file:
        json.dump({
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }, token_file)

    print("Token saved to gmail_token.json")
    print("Add this to your .env file:")
    print(f"GMAIL_CREDENTIALS='{json.dumps(credentials_to_dict(credentials))}'")


if __name__ == "__main__":
    generate_gmail_token()
```

## CLI Patterns Summary

While Phase I used Click/Typer for the main CLI, the project now uses:

1. **Alembic** - Database migrations
2. **UV** - Python package management
3. **Docker Compose** - Local development
4. **kubectl** - Kubernetes operations
5. **Helm** - Kubernetes package management
6. **npm** - Frontend package management

All of these provide CLI interfaces that are essential for development and deployment.
