# Backend Guidelines

## Stack
- FastAPI
- SQLModel (ORM)
- Neon PostgreSQL

## Project Structure
- `app/main.py` - FastAPI app entry point
- `app/models/` - SQLModel database models
- `app/api/` - API route handlers
- `app/db.py` - Database connection

## API Conventions
- All routes under `/api/`
- Return JSON responses
- Use Pydantic models for request/response
- Handle errors with HTTPException

## Database
- Use SQLModel for all database operations
- Connection string from environment variable: DATABASE_URL

## Running
uvicorn app.main:app --reload --port 8000