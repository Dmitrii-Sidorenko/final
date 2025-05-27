from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from typing import List, Optional

from app.core.database import get_db
from ..models import subtask as subtask_model
from ..schemas import subtask as subtask_schema
from ..schemas.subtask import SubtaskFilter
from ..repositories.subtask import SubtaskRepository
from ..repositories.user import UserRepository

class SubtaskService:

    def __init__(self, subtask_repo: SubtaskRepository, user_repo: UserRepository):
        self.subtask_repo = subtask_repo
        self.user_repo = user_repo

    def get_or_404(self, subtask_id: int, raise_exception: bool = True) -> Optional[subtask_model.SubTask]:
        db_subtask = self.subtask_repo.get(subtask_id)
        if db_subtask is None and raise_exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Подзадача не найдена")
        return db_subtask

    def get_by_task(self, task_id: int, skip: int = 0, limit: int = 100, filters: Optional[SubtaskFilter] = None) -> List[subtask_model.SubTask]:
        return self.subtask_repo.get_by_task(task_id, skip, limit, filters)

    def get_all(self, skip: int = 0, limit: int = 100, filters: Optional[SubtaskFilter] = None) -> List[subtask_model.SubTask]:
        return self.subtask_repo.get_all(skip, limit, filters)

    def create(self, subtask_in: subtask_schema.SubtaskCreate, author_id: int) -> subtask_model.SubTask:
        if subtask_in.assignee_id:
            assignee = self.user_repo.get(subtask_in.assignee_id)
            if not assignee:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Исполнитель не найден")

        db_subtask = subtask_model.SubTask(**subtask_in.model_dump(), author_id=author_id)
        return self.subtask_repo.create(db_subtask)

    def update(self, subtask_id: int, subtask_update: subtask_schema.SubtaskUpdate) -> subtask_model.SubTask:
        db_subtask = self.get_or_404(subtask_id)
        update_data = subtask_update.model_dump(exclude_unset=True)
        return self.subtask_repo.update(db_subtask, update_data)

    def delete(self, subtask_id: int) -> None:
        db_subtask = self.get_or_404(subtask_id)
        return self.subtask_repo.delete(db_subtask)

def get_subtask_service(db: Session = Depends(get_db)):
    subtask_repo = SubtaskRepository(db)
    user_repo = UserRepository(db)
    return SubtaskService(subtask_repo, user_repo)