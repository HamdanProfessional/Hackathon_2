"""Notification Service - FastAPI application entry point."""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import test_database_connection
from app.subscriptions import router as subscriptions_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global references to background tasks
background_tasks = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
        - Test database connection
        - Start background workers (due checker, recurring processor)

    Shutdown:
        - Cancel background tasks
    """
    # Startup
    logger.info("Starting Notification Service...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Dapr enabled: {settings.DAPR_ENABLED}")
    logger.info(f"Email enabled: {settings.EMAIL_ENABLED}")

    # Test database connection
    if await test_database_connection():
        logger.info("Database connection successful")
    else:
        logger.warning("Database connection failed - some features may not work")

    # Start background workers
    # NOTE: Background workers disabled for notification service
    # The notification service subscribes to Dapr events instead of polling the database
    # Background workers should be implemented in the main backend service
    logger.info("Background workers disabled (using Dapr event subscriptions instead)")

    yield

    # Shutdown
    logger.info("Shutting down Notification Service...")
    for task in background_tasks:
        task.cancel()
    logger.info("Background workers cancelled")


async def start_due_checker():
    """Start the due checker worker."""
    try:
        from app.workers.due_checker import due_checker_worker
        await due_checker_worker()
    except asyncio.CancelledError:
        logger.info("Due checker worker cancelled")
    except Exception as e:
        logger.error(f"Due checker worker crashed: {e}")


async def start_recurring_processor():
    """Start the recurring task processor worker."""
    try:
        from app.workers.recurring_processor import recurring_task_worker
        await recurring_task_worker()
    except asyncio.CancelledError:
        logger.info("Recurring task processor worker cancelled")
    except Exception as e:
        logger.error(f"Recurring task processor worker crashed: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Notification microservice for Todo App - Event-driven task notifications",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(subscriptions_router, tags=["subscriptions"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "features": {
            "email_notifications": settings.EMAIL_ENABLED,
            "due_checker": True,
            "recurring_processor": True,
            "dapr_subscriptions": settings.DAPR_ENABLED
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/workers/status", tags=["workers"])
async def workers_status():
    """Get status of background workers."""
    return {
        "due_checker": {
            "running": len([t for t in background_tasks if "due_checker" in str(t)]) > 0,
            "interval_seconds": settings.DUE_CHECK_INTERVAL_SECONDS,
            "due_threshold_hours": settings.DUE_THRESHOLD_HOURS
        },
        "recurring_processor": {
            "running": len([t for t in background_tasks if "recurring" in str(t)]) > 0,
            "interval_seconds": settings.RECURRING_CHECK_INTERVAL_SECONDS
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
