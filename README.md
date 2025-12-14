# Todo CRUD Application - Phase II

Full-stack web application for managing tasks with user authentication and data persistence.

## Architecture

This project is organized as a modular monolith with separate frontend and backend:

- **Frontend**: Next.js 15 + React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.13 + SQLAlchemy
- **Database**: PostgreSQL 14+ (Neon serverless)

## Project Structure

```
├── frontend/          # Next.js web application
├── backend/           # FastAPI REST API
├── src/              # Phase I CLI (preserved, not modified)
├── specs/            # Feature specifications and plans
└── README.md         # This file
```

## Quick Start

### Prerequisites

- Python 3.13 or higher
- Node.js 18 or higher
- Neon PostgreSQL account (free tier available)

### Backend Setup

See [backend/README.md](backend/README.md) for detailed instructions.

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
alembic upgrade head
uvicorn app.main:app --reload
```

Backend will run on http://localhost:8000

### Frontend Setup

See [frontend/README.md](frontend/README.md) for detailed instructions.

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local if needed
npm run dev
```

Frontend will run on http://localhost:3000

## Features

- User registration and authentication
- Create, read, update, delete tasks
- Mark tasks as complete/incomplete
- Multi-user support with data isolation
- Persistent data storage (PostgreSQL)
- Responsive web interface

## User Stories

1. **User Registration and Authentication** (P1)
2. **Web-Based Task Creation and Viewing** (P1)
3. **Task Completion Tracking** (P2)
4. **Task Editing and Updating** (P2)
5. **Task Deletion** (P3)
6. **User Data Isolation** (P1)

## Development Workflow

1. **Specification**: See `specs/002-web-app/spec.md`
2. **Planning**: See `specs/002-web-app/plan.md`
3. **Tasks**: See `specs/002-web-app/tasks.md`
4. **Implementation**: Backend-first approach, then frontend integration

## Phase I CLI

The original Phase I console application is preserved in `src/main.py`:

```bash
python src/main.py
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

- **Frontend**: Vercel (recommended)
- **Backend**: Railway, Render, or Fly.io
- **Database**: Neon PostgreSQL

See deployment guides in backend and frontend README files.

## License

Private project for PIAIC Hackathon 2.
