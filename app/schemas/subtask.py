from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import enum

from .user import User  # Импортируйте схему User

class SubTaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"

class SubtaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: SubTaskStatus = SubTaskStatus.TODO

    class Config:
        from_attributes = True

class SubtaskCreate(SubtaskBase):
    task_id: int
    assignee_id: Optional[int] = None

class SubtaskUpdate(SubtaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[SubTaskStatus] = None

class SubtaskInDBBase(SubtaskBase):
    id: int
    author_id: int
    task_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class Subtask(SubtaskInDBBase):
    author: Optional[User] = None
    assignee: Optional[User] = None

    class Config:
        from_attributes = True

class SubtaskFilter(BaseModel):
    title: Optional[str] = None
    status: Optional[SubTaskStatus] = None
    task_id: Optional[int] = None
    assignee_id: Optional[int] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None