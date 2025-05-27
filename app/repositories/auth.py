from typing import Optional

from sqlalchemy.orm import Session

from app.models import User, ResetPasswordToken


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_reset_password_token(self, token: str) -> Optional[ResetPasswordToken]:
        return self.db.query(ResetPasswordToken).filter(ResetPasswordToken.token == token).first()

    def create_reset_password_token(self, token: ResetPasswordToken) -> ResetPasswordToken:
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def delete_reset_password_token(self, token: ResetPasswordToken) -> None:
        self.db.delete(token)
        self.db.commit()