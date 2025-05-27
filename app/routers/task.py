from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ..schemas import task as task_schema
from ..schemas import user as user_schema
from ..services.task import TaskService, get_task_service
from ..core import deps

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[task_schema.Task])
async def get_tasks(
    task_service: TaskService = Depends(get_task_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
    filters: task_schema.TaskFilter = Depends(),
):
    if current_user.is_admin:
        return task_service.get_tasks(filters=filters)
    return task_service.get_tasks(filters=filters, author_id=current_user.id)

@router.get("/{task_id}", response_model=task_schema.Task)
async def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    task = task_service.get_or_404(task_id)
    if not current_user.is_admin and task.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для просмотра этой задачи")
    return task

@router.post("/", response_model=task_schema.Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: task_schema.TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    return task_service.create(task_in, current_user.id)

@router.put("/{task_id}", response_model=task_schema.Task)
async def update_task(
    task_id: int,
    task_update: task_schema.TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    task = task_service.get_or_404(task_id)
    if not current_user.is_admin and task.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для обновления этой задачи")
    return task_service.update(task_id, task_update)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    task = task_service.get_or_404(task_id)
    if not current_user.is_admin and task.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для удаления этой задачи")
    task_service.delete(task_id)
    return