from psycopg2._psycopg import IntegrityError
import string
from pydantic_settings.sources.providers import secrets
from sqlalchemy.orm import Session
import logging
from typing import Optional, List

from fastapi import Depends, HTTPException, status

from app.core.database import get_db
from ..core.email import send_registration_email
from ..repositories.user import UserRepository
from ..schemas import user as user_schema
from ..models.user import User
from ..models import project as project_model
from ..models import user as user_model
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get(self, user_id: int, with_projects: bool = False) -> Optional[User]:
        return self.user_repo.get(user_id, with_projects=with_projects)

    def get_or_404(self, user_id: int) -> User:
        user = self.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.get_by_email(email)

    def get_by_email_or_400(self, email: str) -> User:
        user = self.get_by_email(email)
        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже зарегистрирован")
        return user

    def get_users(self, skip: int = 0, limit: int = 100, with_projects: bool = False) -> List[User]:
        return self.user_repo.get_users(skip, limit, with_projects=with_projects)

    async def add_user_to_project(self, project_id: int, user_email: str, current_user: user_model.User,
                                  db: Session) -> project_model.Project:
        project = self.get_or_404(project_id)
        if project.owner_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Нет прав для добавления пользователей в этот проект")

        user_to_add = self.user_repo.get_by_email(email=user_email)
        new_user = None

        if not user_to_add:
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
            user_create_schema = user_schema.UserCreate(email=user_email, password=password, password_confirm=password)
            new_user_model = user_model.User(
                email=user_create_schema.email,
                hashed_password=get_password_hash(user_create_schema.password),
                is_active=True,
                is_superuser=False,
            )
            try:
                new_user = self.user_repo.create(new_user_model)
                if new_user:
                    await send_registration_email(email=new_user.email, password=password)
                    from ..services.project import get_project_service
                    project_service = get_project_service(db)
                    return await project_service.add_user_to_project_db(project, new_user)
                else:
                    existing_user = self.user_repo.get_by_email(email=user_email)
                    if existing_user:
                        from ..services.project import get_project_service
                        project_service = get_project_service(db)
                        return await project_service.add_user_to_project_db(project, existing_user)
                    else:
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                            detail="Не удалось получить пользователя после попытки создания")
            except IntegrityError:
                existing_user = self.user_repo.get_by_email(email=user_email)
                if existing_user:
                    from ..services.project import get_project_service
                    project_service = get_project_service(db)
                    return await project_service.add_user_to_project_db(project, existing_user)
                else:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                        detail="Ошибка при добавлении пользователя в проект")
        else:
            from ..services.project import get_project_service
            project_service = get_project_service(db)
            return await project_service.add_user_to_project_db(project, user_to_add)

    def update(self, db_user: User, user_update: user_schema.UserUpdate) -> User:
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        return self.user_repo.update(db_user, update_data)


    def delete(self, user_id: int) -> None:
        user = self.get_or_404(user_id)
        self.user_repo.delete(user)

    async def change_password(self, db_user: User, old_password: str, new_password: str) -> User:
        if not verify_password(old_password, db_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный старый пароль")
        hashed_new_password = get_password_hash(new_password)
        update_data = {"hashed_password": hashed_new_password}
        return self.user_repo.update(db_user, update_data)


def get_user_service(db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return UserService(user_repo)