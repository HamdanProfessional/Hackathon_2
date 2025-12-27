"""RecurringTask SQLAlchemy model."""
from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class RecurringTask(Base):
    """RecurringTask model for tasks that repeat on a schedule."""

    __tablename__ = "recurring_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="", nullable=False)
    recurrence_pattern = Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly', 'yearly'
    start_date = Column(Date, nullable=False)  # when to start creating tasks
    end_date = Column(Date, nullable=True)  # optional end date
    next_due_at = Column(Date, nullable=False, index=True)  # next date to create task
    is_active = Column(Boolean, default=True, nullable=False)
    task_priority_id = Column(Integer, ForeignKey("priorities.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="recurring_tasks")
    priority_obj = relationship("Priority", back_populates="recurring_tasks")
    tasks = relationship("Task", back_populates="recurring_task", cascade="all, delete-orphan")

    @property
    def user_id_str(self) -> str:
        """Return user_id as string for serialization."""
        return str(self.user_id)

    def __repr__(self):
        try:
            return f"<RecurringTask(id={self.id}, title={self.title[:30]}, user_id={self.user_id}, pattern={self.recurrence_pattern})>"
        except Exception:
            return f"<RecurringTask(id={getattr(self, 'id', 'Unknown')} [Detached])>"
