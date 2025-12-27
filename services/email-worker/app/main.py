"""Email Worker - FastAPI application with Dapr event subscriptions."""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .database import init_db, close_db
from .subscribers import register_subscribers

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting Email Worker...")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Mail server: {settings.MAIL_SERVER}:{settings.MAIL_PORT}")

    # Initialize database connection
    await init_db()

    yield

    # Shutdown
    logger.info("Shutting down Email Worker...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Email notification service for Todo App with Dapr event subscriptions",
    version="1.0.0",
    lifespan=lifespan
)


# Register Dapr subscribers
register_subscribers(app)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes probes."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }


@app.get("/health/live")
async def liveness():
    """Liveness probe - is the app running?"""
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    """Readiness probe - is the app ready to handle requests?"""
    # Could add database connection check here
    return {"status": "ready"}


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint.

    This endpoint is called by Dapr sidecar to discover subscriptions.
    The actual subscriptions are registered via decorators in subscribers.py
    """
    return {
        "subscriptions": [
            {
                "pubsubname": "todo-pubsub",
                "topic": "task-due-soon",
                "route": "/task-due-soon"
            },
            {
                "pubsubname": "todo-pubsub",
                "topic": "recurring-task-due",
                "route": "/recurring-task-due"
            }
        ]
    }


@app.post("/test-email")
async def test_email():
    """
    Test email endpoint - sends a test email to verify SMTP configuration.

    This endpoint bypasses Dapr and directly sends an email to verify
    the Gmail SMTP configuration is working correctly.
    """
    from .email_service import email_service
    from datetime import datetime

    test_context = {
        "title": "Test Email Notification",
        "due_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "priority": "High",
        "description": "This is a test email to verify the email worker is correctly configured.",
        "category": "Testing",
        "app_url": "https://hackathon2.testservers.online"
    }

    success = await email_service.send_template_email(
        template_name="task-due.html",
        subject="Test Email - Todo App Notification System",
        email=["n00bi2761@gmail.com"],
        context=test_context
    )

    if success:
        return {
            "status": "success",
            "message": "Test email sent successfully to n00bi2761@gmail.com",
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "status": "error",
            "message": "Failed to send test email - check logs for details"
        }


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8003)),
        reload=settings.DEBUG,
        log_level="info"
    )
