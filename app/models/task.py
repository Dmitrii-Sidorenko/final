from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.sql import func
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .project import Project
    from .subtask import SubTask

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    priority = Column(String, nullable=True)

    project = relationship("Project", back_populates="tasks")
    author = relationship("User", back_populates="created_tasks", foreign_keys=[author_id])
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    subtasks = relationship("SubTask", back_populates="task")