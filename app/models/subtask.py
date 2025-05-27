from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.sql import func
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # Исправлено: app.models.user -> .user
    from .task import Task  # Исправлено: app.models.task -> .task

class SubTaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"

class SubTask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SQLEnum(SubTaskStatus), default=SubTaskStatus.TODO)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    priority = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("Task", back_populates="subtasks")
    author = relationship("User", back_populates="created_subtasks", foreign_keys="SubTask.author_id")
    assignee = relationship("User", back_populates="assigned_subtasks", foreign_keys="SubTask.assignee_id")
    owner = relationship("User", back_populates="owned_subtasks", foreign_keys="SubTask.owner_id")