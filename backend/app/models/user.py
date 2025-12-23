"""User SQLAlchemy model."""
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """User model for authentication and data ownership.

    Note: This model has two password fields for historical reasons:
    - hashed_password: Primary field used for authentication (NOT NULL)
    - password_hash: Legacy field from schema migration, kept for compatibility (nullable)

    When creating users, only set hashed_password. The password_hash field can be NULL.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # Primary password field
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=True)  # Legacy field, can be NULL
    preferences = Column(JSON, nullable=True)  # Store user preferences as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships (one-to-many)
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    task_templates = relationship("TaskTemplate", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
