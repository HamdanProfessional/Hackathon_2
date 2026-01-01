# README.md Example

Complete project README with all sections.

```markdown
# Project Name

One-line description of what this project does.

## Overview

2-3 paragraph description of your project's purpose, key features,
and what problem it solves.

## Features

- **Feature 1**: Description with user benefit
- **Feature 2**: Description with user benefit
- **Feature 3**: Description with user benefit

## Tech Stack

### Backend
- **Framework**: FastAPI 0.100+
- **Database**: PostgreSQL (Neon production, SQLite local)
- **ORM**: SQLModel 0.0.8
- **Authentication**: JWT with Better Auth
- **AI**: Groq API (llama-3.1-8b-instant)

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3
- **UI Components**: shadcn/ui

## Installation

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL 14+ (or use Neon)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (`.env`)

```bash
DATABASE_URL=postgresql://user:pass@localhost/dbname
JWT_SECRET=your-secret-key-here
AI_API_KEY=your-groq-api-key
AI_BASE_URL=https://api.groq.com/openai/v1
AI_MODEL=llama-3.1-8b-instant
CORS_ORIGINS=http://localhost:3000
```

### Frontend (`.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Usage

### API Endpoints

**Authentication**:
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

**Tasks**:
- `GET /tasks/` - List tasks (paginated)
- `POST /tasks/` - Create task
- `GET /tasks/{id}` - Get task by ID
- `PATCH /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Development

```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm run test
npm run lint
npm run build
```

## Deployment

### Production URLs

- Frontend: https://frontend.example.com
- Backend: https://api.example.com
- API Docs: https://api.example.com/docs

## License

MIT

## Contributing

Contributions welcome! Please open an issue first.
```
