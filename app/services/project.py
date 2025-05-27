from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from datetime import datetime
import logging
from app.core.database import get_db
from ..core import security
from ..models import project as project_model
from ..models import user as user_model
from ..models import category as category_model
from ..schemas import project as project_schema, user as user_schema
from ..repositories.project import ProjectRepository
from ..repositories.user import UserRepository
from ..core.email import send_registration_email
import secrets
import string
from sqlalchemy.exc import IntegrityError
from app.core.security import get_password_hash
logger = logging.getLogger(__name__)

class ProjectService:

    def __init__(self, project_repo: ProjectRepository, user_repo: UserRepository):
        self.project_repo = project_repo
        self.user_repo = user_repo

    def get_or_404(self, project_id: int, raise_exception: bool = True) -> Optional[project_model.Project]:
        db_project = self.project_repo.get(project_id)
        if db_project is None and raise_exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
        return db_project

    def get_with_tasks(self, project_id: int) -> Optional[project_model.Project]:
        return self.project_repo.get_with_tasks(project_id)

    def get_with_tasks_or_404(self, project_id: int) -> project_model.Project:
        db_project = self.get_with_tasks(project_id)
        if db_project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
        return db_project

    def get_projects(self, filters: project_schema.ProjectFilter) -> List[project_model.Project]:
        return self.project_repo.get_projects(filters)

    def create(self, project_in: project_schema.ProjectCreate, owner_id: int) -> project_model.Project:
        db_project = project_model.Project(
            title=project_in.title,
            description=project_in.description,
            owner_id=owner_id,
            category_id=project_in.category_id,
            icon_id=project_in.icon_id
        )
        return self.project_repo.create(db_project)

    def update(self, project_id: int, project_update: project_schema.ProjectUpdate) -> project_model.Project:
        db_project = self.get_or_404(project_id)
        update_data = project_update.model_dump(exclude_unset=True)
        return self.project_repo.update(db_project, update_data)

    def delete(self, project_id: int) -> None:
        db_project = self.get_or_404(project_id)
        return self.project_repo.delete(db_project)

    def get_category_or_404(self, category_id: int, db: Session) -> category_model.Category:
        db_category = self.project_repo.get_category(category_id)
        if db_category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Категория с ID {category_id} не найдена")
        return db_category

    async def add_user_to_project(self, project_id: int, user_email: str, current_user: user_model.User, db: Session) -> project_model.Project:
        project = self.get_or_404(project_id)
        if project.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для добавления пользователей в этот проект")

        user_to_add = self.user_repo.get_by_email(email=user_email)
        new_user = None

        if not user_to_add:
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
            user_create_schema = user_schema.UserCreate(email=user_email, password=password, password_confirm=password)
            new_user_model = user_model.User(
                email=user_create_schema.email,
                hashed_password=security.get_password_hash(user_create_schema.password),
                is_active=True,
            )
            try:
                new_user = self.user_repo.create(new_user_model)
                if new_user:
                    await send_registration_email(email=new_user.email, password=password)
                    return self.project_repo.add_user_to_project(project, new_user)
                else:
                    existing_user = self.user_repo.get_by_email(email=user_email)
                    if existing_user:
                        return self.project_repo.add_user_to_project(project, existing_user)
                    else:
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось получить пользователя после попытки создания")
            except IntegrityError:
                existing_user = self.user_repo.get_by_email(email=user_email)
                if existing_user:
                    return self.project_repo.add_user_to_project(project, existing_user)
                else:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при добавлении пользователя в проект")
        else:
            return self.project_repo.add_user_to_project(project, user_to_add)

def get_project_service(db: Session = Depends(get_db)):
    project_repo = ProjectRepository(db)
    user_repo = UserRepository(db)
    return ProjectService(project_repo, user_repo)