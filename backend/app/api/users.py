"""User-specific API endpoints."""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.schemas.user import UserPreferencesUpdate
from app.crud import task as task_crud
from app.api.deps import get_current_user

router = APIRouter()


@router.get(
    "/me/export",
    summary="Export all user data",
    description="Export all user tasks and preferences as JSON file",
)
async def export_user_data(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Export all user data as downloadable JSON file.

    Returns a JSON file containing:
    - User profile information
    - All tasks with full details
    - Export metadata
    """
    # Get all tasks for the user
    tasks = await task_crud.get_tasks_by_user(
        db=db,
        user_id=current_user.id,
        limit=None,  # Get all tasks for export
        offset=0
    )

    # Prepare export data
    export_data = {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "preferences": current_user.preferences or {}
        },
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value if task.priority else None,
                "completed": task.completed,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            }
            for task in tasks
        ],
        "export_metadata": {
            "exported_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "total_tasks": len(tasks)
        }
    }

    # Convert to JSON string
    json_data = json.dumps(export_data, indent=2, ensure_ascii=False)

    # Create response with download headers
    filename = f"todo-export-{datetime.utcnow().strftime('%Y-%m-%d')}.json"
    return Response(
        content=json_data,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.patch(
    "/me/preferences",
    summary="Update user preferences",
    description="Update user-specific preferences stored as JSON",
)
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user preferences.

    Accepts partial updates to preferences object.
    Current preferences are merged with new preferences.
    """
    # Merge with existing preferences
    current_prefs = current_user.preferences or {}
    updated_prefs = {**current_prefs, **preferences.preferences}

    # Update user preferences
    current_user.preferences = updated_prefs
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return {"preferences": updated_prefs}


@router.get(
    "/me",
    summary="Get current user profile",
    description="Get current user information and preferences",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get the current user's profile information.

    Returns user data without sensitive information.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "preferences": current_user.preferences or {}
    }