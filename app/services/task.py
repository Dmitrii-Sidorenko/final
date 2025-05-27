from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from typing import List, Optional

from app.core.database import get_db
from ..repositories.task import TaskRepository
from ..repositories.user import UserRepository
from ..repositories.project import ProjectRepository
from ..schemas.task import TaskCreate, TaskUpdate, TaskFilter
from ..models import task as task_model

class TaskService:

    def __init__(self, task_repo: TaskRepository, user_repo: UserRepository, project_repo: ProjectRepository):
        self.task_repo = task_repo
        self.user_repo = user_repo
        self.project_repo = project_repo

    def get_or_404(self, task_id: int, raise_exception: bool = True) -> Optional[task_model.Task]:
        db_task = self.task_repo.get(task_id)
        if db_task is None and raise_exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        return db_task

    def get_tasks(self, filters: TaskFilter, author_id: Optional[int] = None) -> List[task_model.Task]:
        return self.task_repo.get_tasks(filters=filters)

    def create(self, task_in: TaskCreate, owner_id: int) -> task_model.Task:
        project = self.project_repo.get(task_in.project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")

        assignee_id = None
        if task_in.assignee_email:
            assignee = self.user_repo.get_by_email(task_in.assignee_email)
            if not assignee:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Исполнитель с таким email не найден")
            assignee_id = assignee.id
        elif task_in.assignee_id:
            assignee = self.user_repo.get(task_in.assignee_id)
            if not assignee:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Исполнитель не найден")
            assignee_id = assignee.id

        db_task = task_model.Task(
            title=task_in.title,
            description=task_in.description,
            project_id=task_in.project_id,
            author_id=owner_id,
            assignee_id=assignee_id,
            status=task_in.status
        )
        return self.task_repo.create(db_task)
    def update(self, task_id: int, task_update: TaskUpdate) -> task_model.Task:
        db_task = self.get_or_404(task_id)
        update_data = task_update.model_dump(exclude_unset=True)

        if "assignee_email" in update_data:
            assignee = self.user_repo.get_by_email(...)
            if assignee:
                update_data["assignee_id"] = assignee.id
            else:
                raise HTTPException(...)
            del update_data["assignee_email"]
        elif "assignee_id" in update_data:
            assignee = self.user_repo.get(update_data["assignee_id"])
            if not assignee:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Исполнитель не найден")


        return self.task_repo.update(db_task, update_data)

    def delete(self, task_id: int) -> None:
        db_task = self.get_or_404(task_id)
        return self.task_repo.delete(db_task)


def get_task_service(db: Session = Depends(get_db)):
    task_repo = TaskRepository(db)
    user_repo = UserRepository(db)
    project_repo = ProjectRepository(db)
    return TaskService(task_repo, user_repo, project_repo)