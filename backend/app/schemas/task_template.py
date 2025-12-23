"""TaskTemplate Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class TaskTemplateCreate(BaseModel):
    """Schema for task template creation request."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Template title is required"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Default description for tasks created from this template"
    )
    priority_id: int = Field(
        default=2,
        ge=1,
        le=3,
        description="Default priority ID (1=Low, 2=Medium, 3=High)"
    )
    is_recurring: bool = Field(
        default=False,
        description="Whether tasks from this template should be recurring"
    )
    recurrence_pattern: Optional[str] = Field(
        None,
        max_length=100,
        description="Recurrence pattern: daily, weekly, monthly, or yearly"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="List of tags associated with the template"
    )
    subtasks: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of subtask templates (each with title, description)"
    )

    @field_validator('recurrence_pattern')
    @classmethod
    def validate_recurrence_pattern(cls, v, info):
        """Validate recurrence pattern if is_recurring is True."""
        if info.data.get('is_recurring', False) and not v:
            raise ValueError('recurrence_pattern is required when is_recurring is True')
        if v:
            valid_patterns = ['daily', 'weekly', 'monthly', 'yearly']
            if v.lower() not in valid_patterns:
                raise ValueError(f'recurrence_pattern must be one of: {", ".join(valid_patterns)}')
        return v


class TaskTemplateUpdate(BaseModel):
    """Schema for task template update request."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated template title")
    description: Optional[str] = Field(None, max_length=2000, description="Updated template description")
    priority_id: Optional[int] = Field(None, ge=1, le=3, description="Updated priority ID")
    is_recurring: Optional[bool] = Field(None, description="Whether tasks should be recurring")
    recurrence_pattern: Optional[str] = Field(None, max_length=100, description="Recurrence pattern")
    tags: Optional[List[str]] = Field(None, description="Updated list of tags")
    subtasks: Optional[List[Dict[str, Any]]] = Field(None, description="Updated list of subtask templates")


class TaskTemplateResponse(BaseModel):
    """Schema for task template data in responses."""

    id: int
    user_id: str  # UUID string
    title: str
    description: Optional[str]
    priority_id: int
    is_recurring: bool
    recurrence_pattern: Optional[str]
    tags: Optional[List[str]]
    subtasks_template: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_validator('user_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string for serialization."""
        if isinstance(v, UUID):
            return str(v)
        return v

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        """Parse tags from JSON if needed."""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        # If stored as JSON string, parse it
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except:
                return []
        return []

    @field_validator('subtasks_template', mode='before')
    @classmethod
    def parse_subtasks(cls, v):
        """Parse subtasks_template from JSON if needed."""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        # If stored as JSON string, parse it
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except:
                return []
        return []


class TaskFromTemplateRequest(BaseModel):
    """Schema for creating a task from a template with optional overrides."""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Optional override for task title"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional override for task description"
    )
    due_date: Optional[str] = Field(
        None,
        description="Optional due date (YYYY-MM-DD format)"
    )

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        """Validate due date format if provided."""
        if v:
            from datetime import datetime
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('due_date must be in YYYY-MM-DD format')
        return v
