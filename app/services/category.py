from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from typing import Optional, List

from app.core.database import get_db
from ..models import category as category_model
from ..schemas import category as category_schema
from ..repositories.category import CategoryRepository
from ..schemas.category import CategoryFilter

class CategoryService:

    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def get_or_404(self, category_id: int, raise_exception: bool = True) -> Optional[category_model.Category]:
        db_category = self.category_repo.get(category_id)
        if db_category is None and raise_exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")
        return db_category

    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100, filters: Optional[CategoryFilter] = None) -> List[category_model.Category]:
        return self.category_repo.get_by_owner(owner_id, skip, limit, filters)

    def get_all(self, skip: int = 0, limit: int = 100, filters: Optional[CategoryFilter] = None) -> List[category_model.Category]:
        return self.category_repo.get_all(skip, limit, filters)

    def create(self, category_in: category_schema.CategoryCreate, owner_id: int) -> category_model.Category:
        db_category = category_model.Category(name=category_in.name, owner_id=owner_id, color=category_in.color)
        return self.category_repo.create(db_category)

    def update(self, category_id: int, category_update: category_schema.CategoryUpdate) -> category_model.Category:
        db_category = self.get_or_404(category_id)
        update_data = category_update.model_dump(exclude_unset=True)
        return self.category_repo.update(db_category, update_data)

    def delete_cascade(self, category_id: int, db: Session) -> None:
        db_category = self.get_or_404(category_id)

        from ..models import project as project_model
        from ..models import task as task_model
        from ..models import subtask as subtask_model

        projects = db_category.projects
        tasks = db.query(task_model.Task).filter(task_model.Task.project_id.in_([project.id for project in projects])).all()
        for task in tasks:
            db.query(subtask_model.SubTask).filter(subtask_model.SubTask.task_id == task.id).delete()
        db.query(task_model.Task).filter(task_model.Task.project_id.in_([project.id for project in projects])).delete(synchronize_session=False)
        db.query(project_model.Project).filter(project_model.Project.category_id == category_id).delete(synchronize_session=False)
        self.category_repo.delete(db_category)
        db.commit()

def get_category_service(db: Session = Depends(get_db)):
    category_repo = CategoryRepository(db)
    return CategoryService(category_repo)