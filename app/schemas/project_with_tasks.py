# app/schemas/project_with_tasks.py
from typing import Optional, List
from .project import ProjectInDBBase
from .task import Task
from .user import User

class ProjectWithTasks(ProjectInDBBase):
    tasks: Optional[List[Task]] = None
    owner: Optional[User] = None

    class Config:
        from_attributes = True
        orm_mode = True