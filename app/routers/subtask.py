from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..schemas import subtask as subtask_schema
from ..services.subtask import SubtaskService, get_subtask_service
from ..core import deps
from ..schemas import user as user_schema
from ..schemas.subtask import SubtaskFilter

router = APIRouter(prefix="/subtasks", tags=["subtasks"])

@router.get("/", response_model=List[subtask_schema.Subtask])
async def get_subtasks(
    subtask_service: SubtaskService = Depends(get_subtask_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
    filters: SubtaskFilter = Depends(),  # Получаем SubtaskFilter как зависимость
):
    if current_user.is_admin:
        return subtask_service.get_all(filters=filters)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для просмотра всех подзадач.",
        )

@router.get("/{subtask_id}", response_model=subtask_schema.Subtask)
async def get_subtask(
    subtask_id: int,
    subtask_service: SubtaskService = Depends(get_subtask_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    subtask = subtask_service.get_or_404(subtask_id)
    return subtask

@router.post("/", response_model=subtask_schema.Subtask, status_code=status.HTTP_201_CREATED)
async def create_subtask(
    subtask_in: subtask_schema.SubtaskCreate,
    subtask_service: SubtaskService = Depends(get_subtask_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    return subtask_service.create(subtask_in, current_user.id)

@router.put("/{subtask_id}", response_model=subtask_schema.Subtask)
async def update_subtask(
    subtask_id: int,
    subtask_update: subtask_schema.SubtaskUpdate,
    subtask_service: SubtaskService = Depends(get_subtask_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    return subtask_service.update(subtask_id, subtask_update)

@router.delete("/{subtask_id}", status_code=status.HTTP_200_OK)
async def delete_subtask(
    subtask_id: int,
    subtask_service: SubtaskService = Depends(get_subtask_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    subtask_service.delete(subtask_id)
    return {"message": "Подзадача удалена"}