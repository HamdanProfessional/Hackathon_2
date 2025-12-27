"""Task SQLAlchemy model for notification service (read-only)."""
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Priority(Base):
    """Priority model for task priorities."""

    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    level = Column(Integer, nullable=False)  # 1=Low, 2=Medium, 3=High
    color = Column(String(7), nullable=True)  # Hex color code


class Task(Base):
    """Task model for user's todo items."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    priority_id = Column(Integer, ForeignKey("priorities.id"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="", nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    due_date = Column(Date, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(String(100), nullable=True)

    # Phase V: Recurring tasks and notification tracking
    notified = Column(Boolean, default=False, nullable=False)
    recurring_task_id = Column(Integer, ForeignKey("recurring_tasks.id", ondelete="SET NULL"), nullable=True)

    @property
    def user_id_str(self) -> str:
        """Return user_id as string for serialization."""
        return str(self.user_id)

    def __repr__(self):
        try:
            return f"<Task(id={self.id}, title={self.title[:30]}, user_id={self.user_id}, completed={self.completed})>"
        except Exception:
            return f"<Task(id={getattr(self, 'id', 'Unknown')} [Detached])>"


class RecurringTask(Base):
    """RecurringTask model for tasks that repeat on a schedule."""

    __tablename__ = "recurring_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="", nullable=False)
    recurrence_pattern = Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly', 'yearly'
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    next_due_at = Column(Date, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    task_priority_id = Column(Integer, ForeignKey("priorities.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def user_id_str(self) -> str:
        """Return user_id as string for serialization."""
        return str(self.user_id)

    def __repr__(self):
        try:
            return f"<RecurringTask(id={self.id}, title={self.title[:30]}, pattern={self.recurrence_pattern})>"
        except Exception:
            return f"<RecurringTask(id={getattr(self, 'id', 'Unknown')} [Detached])>"


class User(Base):
    """User model for authentication and profile."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
