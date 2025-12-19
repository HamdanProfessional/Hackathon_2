"""Task SQLAlchemy model."""
from datetime import datetime, date

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

    # Relationship to tasks
    tasks = relationship("Task", back_populates="priority_obj")


class Task(Base):
    """Task model for user's todo items."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    priority_id = Column(Integer, ForeignKey("priorities.id"), nullable=True)  # Foreign key to priorities table
    title = Column(String(500), nullable=False)
    description = Column(Text, default="", nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    due_date = Column(Date, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(String(100), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="tasks")
    priority_obj = relationship("Priority", back_populates="tasks")

    @property
    def user_id_str(self) -> str:
        """Return user_id as string for serialization."""
        return str(self.user_id)

    def __repr__(self):
        try:
            return f"<Task(id={self.id}, title={self.title[:30]}, user_id={self.user_id}, completed={self.completed})>"
        except Exception:
            return f"<Task(id={getattr(self, 'id', 'Unknown')} [Detached])>"
