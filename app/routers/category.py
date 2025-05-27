from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from fastapi import status
from sqlalchemy.orm import Session

from app.core.database import get_db
from ..schemas import category as category_schema
from ..schemas import user as user_schema
from ..services.category import CategoryService, get_category_service
from ..core import deps

router = APIRouter(prefix="/categories", tags=["category"])

@router.get("/", response_model=List[category_schema.Category])
async def get_categories(
    category_service: CategoryService = Depends(get_category_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
    filters: category_schema.CategoryFilter = Depends(),
):
    if current_user.is_admin:
        return category_service.get_all(filters=filters)
    return category_service.get_by_owner(owner_id=current_user.id, filters=filters)

@router.get("/{category_id}", response_model=category_schema.Category)
async def get_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    category = category_service.get_or_404(category_id=category_id)
    if not current_user.is_admin and category.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для просмотра этой категории")
    return category

@router.post("/", response_model=category_schema.Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: category_schema.CategoryCreate = Body(..., description="Данные для создания"),
    category_service: CategoryService = Depends(get_category_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    return category_service.create(category_in=category_in, owner_id=current_user.id)

@router.put("/{category_id}", response_model=category_schema.Category)
async def update_category(
    category_id: int,
    category_update: category_schema.CategoryUpdate = Body(..., description="Данные для обновления"),
    category_service: CategoryService = Depends(get_category_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    category = category_service.get_or_404(category_id=category_id)
    if not current_user.is_admin and category.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для обновления этой категории")
    return category_service.update(category_id=category_id, category_update=category_update)

@router.delete("/{category_id}/cascade", status_code=status.HTTP_200_OK)
async def delete_category_cascade(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db),
):
    category = category_service.get_or_404(category_id=category_id)
    if not current_user.is_admin and category.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для удаления этой категории и её содержимого")
    category_service.delete_cascade(category_id=category_id, db=db)
    return {"message": "Категория и всё её содержимое удалены"}