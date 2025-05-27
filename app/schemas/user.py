# app/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator, ValidationInfo
from typing import Optional, List, ForwardRef, TYPE_CHECKING
from uuid import UUID

ALLOWED_PASSWORD_CHARACTERS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&*+-.<=>?@^_")

if TYPE_CHECKING:
    from .project import Project

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar: Optional[int] = None
    is_active: Optional[bool] = True
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str

    @field_validator("password")
    def validate_password_characters(cls, value: str) -> str:
        for char in value:
            if char not in ALLOWED_PASSWORD_CHARACTERS:
                raise ValueError(f"Пароль содержит недопустимый символ: {char}")
        if not 8 <= len(value) <= 16:
            raise ValueError("Пароль должен содержать от 8 до 16 символов.")
        return value

    @field_validator("password_confirm")
    def passwords_match(cls, value: str, info: ValidationInfo) -> str:
        if info.data.get("password") != value:
            raise ValueError("Пароли не совпадают!")
        return value

class UserUpdate(UserBase):
    password: Optional[str] = None
    @field_validator("password")
    def validate_password_characters_optional(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        for char in value:
            if char not in ALLOWED_PASSWORD_CHARACTERS:
                raise ValueError(f"Пароль содержит недопустимый символ: {char}")
        if not 8 <= len(value) <= 16:
            raise ValueError("Пароль должен содержать от 8 до 16 символов.")
        return value

class UserUpdateWithPasswordCheck(UserBase):
    password: Optional[str] = None

class UserInDBBase(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    avatar: Optional[int] = None
    is_active: bool = True
    hashed_password: str
    is_admin: bool

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    def validate_new_password_characters(cls, value: str) -> str:
        for char in value:
            if char not in ALLOWED_PASSWORD_CHARACTERS:
                raise ValueError(f"Пароль содержит недопустимый символ: {char}")
        if not 8 <= len(value) <= 16:
            raise ValueError("Пароль должен содержать от 8 до 16 символов.")
        return value

    @field_validator("confirm_new_password")
    def passwords_match_new(cls, value: str, info: ValidationInfo) -> str:
        if info.data.get("new_password") != value:
            raise ValueError("Новый пароль и подтверждение не совпадают!")
        return value

class Token(BaseModel):
    access_token: str
    token_type: str

class UserWithProjects(UserInDBBase):
    projects: Optional[List[ForwardRef("Project")]] = None

    class Config:
        from_attributes = True