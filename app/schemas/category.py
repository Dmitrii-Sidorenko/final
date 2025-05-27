from pydantic import BaseModel, ConfigDict, constr
from typing import Optional, List

from .project import Project
from .user import User

class CategoryBase(BaseModel):
    name: constr(min_length=1)
    color: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None
    color: Optional[str] = None

class CategoryInDBBase(CategoryBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

class Category(CategoryInDBBase):
    projects: Optional[List[Project]] = None
    owner: Optional[User] = None

    model_config = ConfigDict(from_attributes=True)

# Схема для фильтров
class CategoryFilter(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    owner_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)