"""TaskTemplate SQLAlchemy model for reusable task patterns."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class TaskTemplate(Base):
    """TaskTemplate model for saving and reusing common task patterns.

    Users can create templates from their tasks to quickly recreate
    similar tasks in the future. Templates store title, description,
    priority, recurrence settings, tags, and optional subtask templates.

    Attributes:
        id: Primary key
        user_id: Owner user ID (foreign key to users table)
        title: Template title
        description: Default description for tasks created from this template
        priority_id: Default priority ID (1=Low, 2=Medium, 3=High)
        is_recurring: Whether tasks from this template should be recurring
        recurrence_pattern: Recurrence pattern (daily, weekly, monthly, yearly)
        tags: JSON array of tags associated with the template
        subtasks_template: JSON array of subtask templates
        created_at: Timestamp when template was created
        updated_at: Timestamp when template was last updated
    """

    __tablename__ = "task_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    priority_id = Column(Integer, nullable=False, default=2)  # Default Medium
    is_recurring = Column(Boolean, nullable=False, default=False)
    recurrence_pattern = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)  # JSON array of tag strings
    subtasks_template = Column(JSON, nullable=True)  # JSON array of subtask objects
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship to User
    owner = relationship("User", back_populates="task_templates")

    def __repr__(self):
        return f"<TaskTemplate(id={self.id}, title={self.title}, user_id={self.user_id})>"
