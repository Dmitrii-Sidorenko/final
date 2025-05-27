from fastapi import APIRouter, Depends, HTTPException, status
import logging
from typing import List

from ..schemas import user as user_schema
from app.core import deps
from ..services.user import UserService, get_user_service
from app.core.security import verify_password

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)

@router.get("/me", response_model=user_schema.UserWithProjects)
async def get_current_user(
    current_user: user_schema.User = Depends(deps.get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Получение информации о текущем пользователе с его проектами."""
    user_schema.UserWithProjects.model_rebuild()
    return user_service.get(current_user.id, with_projects=True)

@router.patch("/me", response_model=user_schema.User)
async def update_current_user(
    user_in: user_schema.UserUpdateWithPasswordCheck,
    user_service: UserService = Depends(get_user_service),
    current_user: user_schema.User = Depends(deps.get_current_user),
):
    """Обновление информации о текущем пользователе."""
    return user_service.update(db_user=current_user, user_update=user_in)

@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: user_schema.ChangePassword,
    user_service: UserService = Depends(get_user_service),
    current_user: user_schema.User = Depends(deps.get_current_user)
):
    """Изменение пароля текущего пользователя."""
    await user_service.change_password(current_user, password_change.old_password, password_change.new_password)
    return {"message": "Пароль успешно изменен"}

@router.get("/{user_id}", response_model=user_schema.UserWithProjects)
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для просмотра информации о пользователе"
        )
    user = user_service.get(user_id, with_projects=True)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    user_schema.UserWithProjects.model_rebuild()
    return user

@router.get("/all/projects", response_model=List[user_schema.UserWithProjects], dependencies=[Depends(deps.get_current_active_admin)])
async def get_all_users_with_projects_for_admin(user_service: UserService = Depends(get_user_service)):
    return user_service.get_users(with_projects=True)

@router.delete("/{user_id}", response_model=user_schema.User, dependencies=[Depends(deps.get_current_active_admin)])
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    user = user_service.get_or_404(user_id)
    user_service.delete(user_id)
    return user