# app/schemas/project.py
from typing import Optional, List, ForwardRef, TYPE_CHECKING
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

if TYPE_CHECKING:
    from .user import UserBase

UserBase = ForwardRef("UserBase")

class ProjectBase(BaseModel):
    title: str = Field(max_length=100)
    description: Optional[str] = None
    category_id: int
    icon_id: Optional[int] = None

    class Config:
        from_attributes = True

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    title: Optional[str] = Field(max_length=100)
    description: Optional[str] = None
    category_id: Optional[int] = None
    icon_id: Optional[int] = None
    invitee_email: Optional[EmailStr] = None

class ProjectInDBBase(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectFilter(BaseModel):
    category_id: Optional[int] = None
    owner_id: Optional[int] = None
    title: Optional[str] = None
    created_at_start: Optional[datetime] = None
    created_at_end: Optional[datetime] = None
    description: Optional[str] = None

class Project(ProjectInDBBase):
    owner: Optional[ForwardRef("UserBase")] = None

    class Config:
        from_attributes = True
        orm_mode = True