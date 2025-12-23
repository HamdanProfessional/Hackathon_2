"""Subtask SQLAlchemy model."""
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Subtask(Base):
    """Subtask model for breaking down tasks into smaller steps."""

    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to parent task
    task = relationship("Task", back_populates="subtasks")

    def __repr__(self):
        return f"<Subtask(id={self.id}, title={self.title[:30]}, task_id={self.task_id}, completed={self.completed})>"
