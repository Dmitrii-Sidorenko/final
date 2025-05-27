from datetime import datetime, timedelta, timezone
import logging
from typing import Optional

from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.email import send_reset_password_email
from ..repositories.reset_password_token import ResetPasswordTokenRepository
from ..repositories.user import UserRepository
from ..schemas.reset_password import ResetPassword, ResetPasswordRequest
from ..schemas.user import UserUpdate

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ResetPasswordService:

    def __init__(self, token_repo: ResetPasswordTokenRepository, user_repo: UserRepository):
        self.token_repo = token_repo
        self.user_repo = user_repo

    async def request_reset_password(self, request: ResetPasswordRequest, db: Session):

        user = self.user_repo.get_by_email(request.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

        reset_code = await send_reset_password_email(email=request.email)
        expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.token_repo.create(email=request.email, user_id=user.id, plain_token=reset_code, expires=expires_at)
        return {"message": "Код восстановления пароля отправлен на ваш email"}

    async def confirm_reset_password(self, reset_password: ResetPassword, db: Session):
        token_value = reset_password.token
        logger.info(f"Попытка подтверждения сброса пароля с кодом: {token_value}")
        db_token = self.token_repo.get_by_token_value(token_value)
        if not db_token:
            logger.warning(f"Не найден токен для кода: {token_value}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Неверный код")

        logger.info(f"Найден токен в БД: {db_token.token}, expires: {db_token.expires}")
        if datetime.now(timezone.utc) > db_token.expires.replace(tzinfo=timezone.utc):
            self.token_repo.delete(db_token.token)
            logger.warning(f"Срок действия токена истек: {db_token.token}")
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Токен истек")

        user = self.user_repo.get(db_token.user_id)
        if not user:
            logger.error(f"Не найден пользователь с ID: {db_token.user_id} для токена: {db_token.token}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

        hashed_password = pwd_context.hash(reset_password.new_password)
        user.hashed_password = hashed_password
        self.user_repo.update(user, {"hashed_password": user.hashed_password})
        self.token_repo.delete(db_token.token)
        logger.info(f"Пароль пользователя {user.email} успешно сброшен.")
        return {"message": "Пароль успешно изменен"}

def get_reset_password_service(db: Session = Depends(get_db)):
    token_repo = ResetPasswordTokenRepository(db)
    user_repo = UserRepository(db)
    return ResetPasswordService(token_repo, user_repo)