from sqlalchemy.orm import Session, joinedload
import logging
from typing import Optional, List
from sqlalchemy.exc import IntegrityError

from ..models.user import User

logger = logging.getLogger(__name__)

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int, with_projects: bool = False) -> Optional[User]:
        logger.info(f"Получение пользователя с ID: {user_id}, с проектами: {with_projects}")
        query = self.db.query(User).filter(User.id == user_id)
        if with_projects:
            query = query.options(joinedload(User.projects))
        return query.first()

    def get_by_email(self, email: str) -> Optional[User]:
        logger.info(f"Получение пользователя с email: {email}")
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self, skip: int = 0, limit: int = 100, with_projects: bool = False) -> List[User]:
        logger.info(f"Получение списка пользователей, пропуская: {skip}, лимит: {limit}, с проектами: {with_projects}")
        query = self.db.query(User).offset(skip).limit(limit)
        if with_projects:
            query = query.options(joinedload(User.projects))
        return query.all()

    def create(self, user: User) -> User:
        logger.info(f"Создание нового пользователя с email: {user.email}")
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Пользователь с email: {user.email} успешно создан, ID: {user.id}")
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise IntegrityError("Пользователь с таким email уже существует", params=e.params, orig=e.orig) from e

    def update(self, db_user: User, user_update_data: dict) -> User:
        logger.info(f"Обновление пользователя с ID: {db_user.id}, email: {db_user.email}")
        logger.info(f"Данные для обновления пользователя {db_user.email}: {user_update_data}")
        for key, value in user_update_data.items():
            logger.info(f"Установка атрибута {key} в значение: {value} для пользователя {db_user.email}")
            setattr(db_user, key, value)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"Состояние пользователя {db_user.email} обновлено.")
        return db_user

    def delete(self, user: User) -> None:
        logger.warning(f"Попытка удаления пользователя с ID: {user.id}, email: {user.email}")
        self.db.delete(user)
        self.db.commit()
        logger.warning(f"Пользователь с ID: {user.id}, email: {user.email} успешно удален.")