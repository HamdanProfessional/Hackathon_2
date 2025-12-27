"""TaskEventLog SQLAlchemy model for notification service."""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class TaskEventLog(Base):
    """TaskEventLog model for audit trail of task events."""

    __tablename__ = "task_event_log"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # 'created', 'updated', 'completed', 'deleted', 'due_soon'
    event_data = Column(JSONB, nullable=True)  # store event payload
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        try:
            return f"<TaskEventLog(id={self.id}, task_id={self.task_id}, event_type={self.event_type})>"
        except Exception:
            return f"<TaskEventLog(id={getattr(self, 'id', 'Unknown')} [Detached])>"
