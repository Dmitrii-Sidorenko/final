from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import enum
from .project import Project  # Импорт схемы Project
from .user import UserBase  # Импорт базовой схемы User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # Import the full User schema if needed for type hinting

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"

class TaskBase(BaseModel):
    title: str = Field(max_length=100)
    description: Optional[str] = Field(max_length=10000, default=None)
    due_date: Optional[datetime] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Optional[str] = None

class TaskCreate(TaskBase):
    project_id: int
    assignee_id: Optional[int] = None
    assignee_email: Optional[EmailStr] = None

class TaskUpdate(TaskBase):
    title: Optional[str] = Field(max_length=100, default=None)
    description: Optional[str] = Field(max_length=10000, default=None)
    due_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    assignee_email: Optional[EmailStr] = None
    priority: Optional[str] = None

class TaskInDBBase(TaskBase):
    id: int
    project_id: int
    author_id: int
    assignee_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Task(TaskInDBBase):
    project: Optional[Project] = None
    assignee: Optional[UserBase] = None
    author: Optional[UserBase] = None

    class Config:
        from_attributes = True

class TaskFilter(BaseModel):
    project_id: Optional[int] = None
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    created_at_start: Optional[datetime] = None
    created_at_end: Optional[datetime] = None