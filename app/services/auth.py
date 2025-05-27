from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
import secrets
import string

from app.core.database import get_db
from ..repositories.auth import AuthRepository
from ..repositories.user import UserRepository
from ..services.user import UserService
from ..schemas import user as user_schema
from ..models import User, ResetPasswordToken
from app.core.security import get_password_hash, verify_password
from app.core.token import create_access_token
from app.core.config import settings

class AuthService:

    def __init__(self, auth_repo: AuthRepository, user_service: UserService):
        self.auth_repo = auth_repo
        self.user_service = user_service

    def register_user(self, user: user_schema.UserCreate) -> User:
        if self.auth_repo.get_user_by_email(user.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже зарегистрирован")

        hashed_password = get_password_hash(user.password)
        new_user = User(email=user.email, hashed_password=hashed_password, is_active=True)
        return self.auth_repo.create_user(new_user)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.auth_repo.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user_id: int) -> str:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(data={"sub": str(user_id)}, expires_delta=access_token_expires)

    def create_reset_password_token(self, email: str, user_id: int, token_value: str) -> ResetPasswordToken:
        old_token = self.auth_repo.get_reset_password_token(token_value)
        if old_token and old_token.email == email:
            self.auth_repo.delete_reset_password_token(old_token)

        expires_at = datetime.utcnow() + timedelta(hours=24)
        new_token = ResetPasswordToken(email=email, user_id=user_id, token=token_value, expires=expires_at)
        return self.auth_repo.create_reset_password_token(new_token)

    def get_reset_password_token(self, token: str) -> Optional[ResetPasswordToken]:
        return self.auth_repo.get_reset_password_token(token)

    def reset_user_password(self, token_value: str, new_password: str) -> User:
        db_token = self.get_reset_password_token(token_value)
        if not db_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недействительный код восстановления пароля")
        if db_token.expires < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Срок действия кода восстановления пароля истек")

        user = self.user_service.get_by_email_or_raise(db_token.email)
        user.hashed_password = get_password_hash(new_password)
        self.auth_repo.create_user(user)
        self.auth_repo.delete_reset_password_token(db_token)
        return user

    def generate_reset_password_token(self) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(32))

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.auth_repo.get_user_by_email(email)

def get_auth_service(db: Session = Depends(get_db)):
    auth_repo = AuthRepository(db)
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return AuthService(auth_repo, user_service)