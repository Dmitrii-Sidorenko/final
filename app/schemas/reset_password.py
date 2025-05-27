# app/schemas/reset_password.py
from datetime import datetime
from pydantic import BaseModel, field_validator,EmailStr
from typing import Optional
from pydantic_core.core_schema import ValidationInfo

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str
    confirm_new_password: str

    @field_validator("confirm_new_password")
    @classmethod
    def passwords_match(cls, value: str, info: ValidationInfo) -> str:
        if info.data.get("new_password") != value:
            raise ValueError("Новые пароли не совпадают!")
        return value

class ResetPasswordToken(BaseModel):
    token: str
    email: str
    user_id: int
    created_at: datetime
    expires: datetime

    class Config:
        from_attributes = True