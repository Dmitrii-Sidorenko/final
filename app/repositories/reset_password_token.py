from typing import Optional
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.reset_password_token import ResetPasswordToken as ResetPasswordTokenModel

logger = logging.getLogger(__name__)

class ResetPasswordTokenRepository:

    def __init__(self, db: Session):

        self.db = db

    def create(self, email: str, user_id: int, plain_token: str, expires: datetime) -> ResetPasswordTokenModel:
        db_token = ResetPasswordTokenModel(email=email, token=plain_token, user_id=user_id, expires=expires)
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_by_token_value(self, token_value: str) -> Optional[ResetPasswordTokenModel]:
        logger.info(f"Попытка поиска токена со значением: '{token_value}'")
        db_token = self.db.query(ResetPasswordTokenModel).filter(ResetPasswordTokenModel.token == token_value).first()
        if db_token:
            logger.info(f"Найден токен в БД со значением: '{db_token.token}', expires: {db_token.expires}")
        else:
            logger.warning(f"Токен со значением '{token_value}' не найден в БД.")
        return db_token

    def get_by_email(self, email: str) -> Optional[ResetPasswordTokenModel]:
        return self.db.query(ResetPasswordTokenModel).filter(ResetPasswordTokenModel.email == email).first()

    def delete(self, token: str) -> bool:
        db_token = self.db.query(ResetPasswordTokenModel).filter(ResetPasswordTokenModel.token == token).first()
        if db_token:
            self.db.delete(db_token)
            self.db.commit()
            return True
        return False

    def check_expiration(self, db_token: ResetPasswordTokenModel) -> bool:
        now_utc = datetime.now(timezone.utc)
        expires_utc = db_token.expires.replace(tzinfo=timezone.utc)
        logger.info(f"Текущее UTC время: {now_utc}, Время истечения UTC: {expires_utc}")
        if now_utc > expires_utc:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Токен истек")
        return True