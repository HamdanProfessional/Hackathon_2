# QUICKSTART.md

Get Evolution Todo - Phase II running in minutes!

## Prerequisites

- Node.js 18+ and npm
- Python 3.13+
- Docker and Docker Compose (optional but recommended)
- Git

## Option 1: Docker Compose (Recommended)

1. **Clone and navigate to the project**
   ```bash
   git clone <repository-url>
   cd hackathon-2
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add:
   - `DATABASE_URL`: Get from [Neon](https://neon.tech) (Connection string)
   - `JWT_SECRET`: Generate with `openssl rand -base64 32`
   - `BETTER_AUTH_SECRET`: Use the same value as JWT_SECRET
   - `BETTER_AUTH_URL`: `http://localhost:3000`
   - `NEXT_PUBLIC_API_URL`: `http://localhost:8000`

3. **Start everything with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Run database migrations**
   ```bash
   # In a new terminal
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Option 2: Manual Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file in backend/
   DATABASE_URL=postgresql://user:password@host:port/dbname
   JWT_SECRET=your-secret-key-here
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the FastAPI server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory (new terminal)**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create environment file**
   ```bash
   # Create .env.local in frontend/
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

## First Run

1. **Open the application** at http://localhost:3000
2. **Register a new account** using the signup form
3. **Login** with your credentials
4. **Create your first task** and explore the features!

## Features to Try

- ✅ Create, edit, and delete tasks
- 🔍 Search and filter tasks
- 🎨 Toggle between light and dark themes
- 📥 Export your tasks to JSON
- 📱 View on mobile devices

## Troubleshooting

### Database Connection Issues
- Ensure your `DATABASE_URL` is correct
- Check if your Neon database is active
- Verify network connectivity

### Port Already in Use
```bash
# Kill processes on port 3000
npx kill-port 3000

# Kill processes on port 8000
npx kill-port 8000
```

### CORS Errors
- Make sure both frontend and backend are running
- Verify `NEXT_PUBLIC_API_URL` matches the backend URL
- Check CORS configuration in `backend/app/main.py`

### Frontend Build Errors
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

### Backend Import Errors
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
# Follow activation and install steps again
```

## Development Tips

- Use the API docs at `/docs` to test endpoints directly
- Check browser console for frontend errors
- Backend logs show API request details
- All database migrations are in `backend/alembic/versions/`

## Next Steps

- Read the full [README.md](./README.md) for detailed documentation
- Check `specs/` directory for feature specifications
- Explore `history/` for architectural decisions and prompt history

---

Need help? Check the README.md or open an issue on GitHub.