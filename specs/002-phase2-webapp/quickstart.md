# Quick Start Guide: Phase II Development

## Prerequisites

- Node.js 18+ and npm
- Python 3.13+
- Docker and Docker Compose
- Neon PostgreSQL account (for production)

## Local Development Setup

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# JWT Secret (generate a secure random string)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# Database URL (for local development with Docker)
DATABASE_URL=postgresql://postgres:password@localhost:5432/todos

# Better Auth Configuration
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
```

### 2. Start Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

This will start:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### 3. Database Initialization

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# (Optional) Create a test user
docker-compose exec backend python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text('INSERT INTO users (email, hashed_password) VALUES (:email, :hash)'))
    conn.commit()
"
```

## Development Workflow

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Key files:
- `app/layout.tsx` - Root layout with theme provider
- `app/dashboard/page.tsx` - Main dashboard
- `components/ui/` - Reusable UI components
- `lib/api.ts` - API client functions

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Key files:
- `app/main.py` - FastAPI application entry
- `app/models/` - SQLModel database models
- `app/api/` - API route handlers
- `app/core/` - Configuration and security

### Database Changes

1. Update SQLModel in `app/models/`
2. Generate migration:
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "description"
   ```
3. Apply migration:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Testing

### Frontend Tests
```bash
cd frontend
npm test
npm run test:e2e  # Playwright end-to-end tests
```

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

## Production Deployment

### Neon Database Setup

1. Create a new project in Neon Console
2. Copy the connection string
3. Update `.env`:
   ```bash
   DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
   ```

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

### Backend (Railway/Render)

1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically on push to main

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000, 8000, and 5432 are available
2. **JWT errors**: Verify JWT_SECRET matches between frontend and backend
3. **Database connection**: Check PostgreSQL container is running
4. **CORS errors**: Verify API_URL environment variable

### Debug Commands

```bash
# Check container status
docker-compose ps

# Restart services
docker-compose restart

# View backend logs
docker-compose logs backend

# Access database
docker-compose exec postgres psql -U postgres -d todos
```

## Development Tips

### Code Style

- Frontend: Use Prettier with TypeScript strict mode
- Backend: Use Black formatter with isort
- Pre-commit hooks ensure consistent formatting

### Performance

- Frontend: Use React Query for server state caching
- Backend: Implement database query optimization
- Database: Add indexes for frequently queried fields

### Security

- Never commit `.env` files
- Use HTTPS in production
- Rotate JWT secrets regularly
- Implement rate limiting on API endpoints