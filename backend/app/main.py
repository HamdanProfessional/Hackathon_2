"""FastAPI application instance and configuration."""
import logging
import os
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.database import create_tables
# Import all models to ensure they're registered with Base.metadata
from app.models import user, task, conversation, message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting up application...")

    # Try to create database tables but don't fail if it doesn't work
    try:
        await create_tables()
        logger.info("Database setup complete")
    except Exception as e:
        logger.warning(f"Database setup failed, but continuing: {e}")

    logger.info("Application startup complete")
    yield

    # Shutdown
    logger.info("Shutting down application...")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="REST API for Todo CRUD application with user authentication and AI chat assistant",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Configure rate limiting exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Add security headers
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Add HSTS header only in production and over HTTPS
    if os.getenv("ENVIRONMENT") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    return response

# Add HTTPS redirect middleware (only in production)
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS if hasattr(settings, 'ALLOWED_HOSTS') else ["*"]
)

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with clear messages."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Please check your input",
            "details": errors
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected server errors."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Todo AI Assistant API",
        "version": "3.0.0",
        "phase": "III - AI Chatbot",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}

@app.get("/test-db", tags=["Test"])
async def test_database():
    """Test database connection."""
    try:
        from app.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return {"status": "database connected", "result": result.scalar()}
    except Exception as e:
        return {"status": "database error", "error": str(e)}

@app.get("/test-tables", tags=["Test"])
async def test_tables():
    """Test if database tables exist."""
    try:
        from app.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            # Check if users table exists
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
            )
            users_exist = result.scalar()

            # Check if tasks table exists
            result = await conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tasks')")
            )
            tasks_exist = result.scalar()

            return {
                "status": "tables checked",
                "users_table": users_exist,
                "tasks_table": tasks_exist
            }
    except Exception as e:
        return {"status": "error checking tables", "error": str(e)}

@app.post("/test-register", tags=["Test"])
async def test_register():
    """Test user registration directly."""
    try:
        from app.database import get_db
        from app.crud import user as user_crud
        from app.schemas.user import UserCreate
        from app.models.user import User
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import text

        # Check what columns exist in users table
        async for db in get_db():
            result = await db.execute(
                text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                """)
            )
            columns = result.fetchall()

            # Check if hashed_password column exists
            has_hashed_password = any(col[0] == 'hashed_password' for col in columns)
            has_preferences = any(col[0] == 'preferences' for col in columns)

            # Add missing columns
            columns_added = []

            if not has_hashed_password:
                try:
                    await db.execute(
                        text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)")
                    )
                    columns_added.append("hashed_password")
                except Exception as alter_error:
                    return {
                        "status": "error",
                        "message": f"Failed to add hashed_password column: {alter_error}",
                        "existing_columns": [col[0] for col in columns],
                        "schema_issue": True
                    }

            if not has_preferences:
                try:
                    await db.execute(
                        text("ALTER TABLE users ADD COLUMN preferences JSONB")
                    )
                    columns_added.append("preferences")
                except Exception as alter_error:
                    return {
                        "status": "error",
                        "message": f"Failed to add preferences column: {alter_error}",
                        "existing_columns": [col[0] for col in columns],
                        "schema_issue": True
                    }

            # Check if id column is auto-incrementing
            has_id = any(col[0] == 'id' for col in columns)
            if has_id:
                # Create a sequence if it doesn't exist
                try:
                    await db.execute(text("""
                        CREATE SEQUENCE IF NOT EXISTS users_id_seq
                        OWNED BY users.id
                    """))
                    await db.execute(text("""
                        ALTER TABLE users
                        ALTER COLUMN id
                        SET DEFAULT nextval('users_id_seq')
                    """))
                    columns_added.append("id sequence")
                except Exception as seq_error:
                    # Sequence might already exist or table might be empty
                    pass

            if columns_added:
                await db.commit()
                return {
                    "status": "success",
                    "message": f"Added columns to users table: {', '.join(columns_added)}",
                    "columns_before": [col[0] for col in columns],
                    "columns_added": columns_added,
                    "action": "Schema updated successfully"
                }

            # Create test user data
            user_data = UserCreate(
                email="test789@example.com",  # Use new email
                password="testpass123"  # 8 characters minimum
            )

            # Check if user already exists
            existing_user = await user_crud.get_user_by_email(db, user_data.email)
            if existing_user:
                return {
                    "status": "error",
                    "message": "User already exists",
                    "user_id": existing_user.id,
                    "columns": [col[0] for col in columns],
                    "has_hashed_password": has_hashed_password,
                    "has_preferences": has_preferences
                }

            # Create user
            user = await user_crud.create_user(db, user_data)

            return {
                "status": "success",
                "user_id": user.id,
                "email": user.email,
                "columns": [col[0] for col in columns],
                "has_hashed_password": has_hashed_password,
                "has_preferences": has_preferences,
                "password_hashed": bool(user.hashed_password) if hasattr(user, 'hashed_password') else "N/A"
            }
            break  # Exit after first iteration

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/test-direct-user", tags=["Test"])
async def test_direct_user():
    """Test creating a user directly with SQL."""
    try:
        from app.database import engine
        from app.utils.security import hash_password
        from sqlalchemy import text
        import uuid

        # Hash password
        hashed = hash_password("testpass123")

        # Generate a UUID
        user_id = str(uuid.uuid4())

        # Insert user directly with SQL
        async with engine.begin() as conn:
            # Insert user with explicit UUID and all required fields
            result = await conn.execute(text("""
                INSERT INTO users (id, email, password_hash, name, hashed_password, created_at)
                VALUES (:id, :email, :password, :name, :password, NOW())
                RETURNING id
            """), {"id": user_id, "email": "test456@example.com", "password": hashed, "name": "Test User"})

            inserted_id = result.scalar()

            await conn.commit()

            return {
                "status": "success",
                "message": "User created successfully",
                "user_id": inserted_id,
                "email": "test456@example.com"
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/test-schema", tags=["Test"])
async def test_schema():
    """Check database schema."""
    try:
        from app.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()

            return {
                "status": "success",
                "table": "users",
                "columns": [{"name": col[0], "type": col[1], "nullable": col[2]} for col in columns]
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/test-tasks-schema", tags=["Test"])
async def test_tasks_schema():
    """Check tasks table schema."""
    try:
        from app.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()

            return {
                "status": "success",
                "table": "tasks",
                "columns": [
                    {"name": col[0], "type": col[1], "nullable": col[2], "default": col[3]}
                    for col in columns
                ]
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/test-priority-table", tags=["Test"])
async def test_priority_table():
    """Check if priority table exists."""
    try:
        from app.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            # Check if priority table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'priorities'
                );
            """))
            table_exists = result.scalar()

            result2 = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'task_priorities'
                );
            """))
            table2_exists = result2.scalar()

            return {
                "status": "success",
                "priorities_table": table_exists,
                "task_priorities_table": table2_exists
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/test-priorities-data", tags=["Test"])
async def test_priorities_data():
    """Check what's in the priorities table."""
    try:
        from app.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT * FROM priorities ORDER BY id;
            """))
            rows = result.fetchall()

            return {
                "status": "success",
                "priorities": [dict(row._mapping) for row in rows]
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/test-create-priorities", tags=["Test"])
async def test_create_priorities():
    """Create default priorities if they don't exist."""
    try:
        from app.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            # First, check the table schema
            result = await conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'priorities'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()

            # Check if priorities exist
            result = await conn.execute(text("SELECT COUNT(*) FROM priorities"))
            count = result.scalar()

            if count == 0:
                # Insert default priorities with level and color
                await conn.execute(text("""
                    INSERT INTO priorities (id, name, level, color) VALUES
                    (1, 'Low', 1, '#28a745'),
                    (2, 'Medium', 2, '#ffc107'),
                    (3, 'High', 3, '#dc3545')
                """))
                await conn.commit()
                return {
                    "status": "success",
                    "message": "Default priorities created",
                    "columns": [{"name": col[0], "type": col[1]} for col in columns]
                }
            else:
                return {
                    "status": "success",
                    "message": f"Priorities already exist ({count} rows)",
                    "columns": [{"name": col[0], "type": col[1]} for col in columns]
                }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/test-create-task", tags=["Test"])
async def test_create_task_direct():
    """Test creating a task directly with SQL."""
    try:
        from app.database import engine
        from sqlalchemy import text

        async with engine.begin() as conn:
            # Get an existing user
            result = await conn.execute(text("""
                SELECT id FROM users LIMIT 1
            """))
            user_row = result.scalar_one_or_none()

            if not user_row:
                return {"status": "error", "message": "No users found"}

            user_uuid = str(user_row)

            # Insert task
            result2 = await conn.execute(text("""
                INSERT INTO tasks (user_id, title, description, priority_id, completed, created_at, updated_at)
                VALUES (:user_id, :title, :description, :priority_id, false, NOW(), NOW())
                RETURNING id
            """), {"user_id": user_uuid, "title": "Test Task", "description": "Test Description", "priority_id": 2})

            task_id = result2.scalar()

            await conn.commit()

            return {
                "status": "success",
                "message": "Task created successfully",
                "user_id": user_uuid,
                "task_id": task_id
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/test-create-task-crud", tags=["Test"])
async def test_create_task_crud():
    """Test creating a task via CRUD operations."""
    try:
        from app.database import get_db
        from app.crud import task as task_crud
        from app.schemas.task import TaskCreate

        async for db in get_db():
            # Get an existing user
            from sqlalchemy import text
            result = await db.execute(text("""
                SELECT id FROM users LIMIT 1
            """))
            user_row = result.scalar_one_or_none()

            if not user_row:
                return {"status": "error", "message": "No users found"}

            user_uuid = str(user_row)

            # Create task data
            task_data = TaskCreate(
                title="Test CRUD Task",
                description="Testing CRUD task creation",
                priority_id=2
            )

            # Create task via CRUD
            task = await task_crud.create_task(db, task_data, user_uuid)

            return {
                "status": "success",
                "message": "Task created successfully via CRUD",
                "task_id": task.id,
                "priority_obj": task.priority_obj.name if task.priority_obj else None
            }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/test-auth", tags=["Test"])
async def test_auth(authorization: str = Header(None)):
    """Test authentication flow"""
    return {
        "authorization": authorization,
        "has_auth": authorization is not None,
        "auth_length": len(authorization) if authorization else 0
    }


# Import routers
from app.api import auth, tasks, users, chat

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
