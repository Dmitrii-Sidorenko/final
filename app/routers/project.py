from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime
import logging

from sqlalchemy.orm import Session
from app.core.database import get_db
from ..core import deps
from ..schemas import project as project_schema
from ..schemas import user as user_schema
from ..schemas.project_with_tasks import ProjectWithTasks
from ..services.project import ProjectService, get_project_service

router = APIRouter(prefix="/projects", tags=["projects"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[project_schema.Project])
async def get_projects(
    project_service: ProjectService = Depends(get_project_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
    filters: project_schema.ProjectFilter = Depends(),  # Получаем ProjectFilter как зависимость
):
    if current_user.is_admin:
        return project_service.get_projects(filters=filters)
    else:
        filters.owner_id = current_user.id
        return project_service.get_projects(filters=filters)

@router.get("/{project_id}", response_model=ProjectWithTasks)
async def get_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    project = project_service.get_with_tasks_or_404(project_id)
    if not current_user.is_admin and project.owner_id != current_user.id and current_user not in project.participants:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для просмотра этого проекта")
    return project

@router.post("/", response_model=project_schema.Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: project_schema.ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db),
):
    project_service.get_category_or_404(project_in.category_id, db)
    return project_service.create(project_in, current_user.id)

@router.put("/{project_id}", response_model=project_schema.Project)
async def update_project(
    project_id: int,
    project_update: project_schema.ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    project = project_service.get_or_404(project_id)
    if not current_user.is_admin and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для обновления этого проекта")
    return project_service.update(project_id, project_update)

@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    project = project_service.get_or_404(project_id)
    if not current_user.is_admin and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для удаления этого проекта")
    project_service.delete(project_id)
    return {"message": "Проект удален"}

@router.post("/{project_id}/add_user", response_model=project_schema.Project)
async def add_user_to_project(
    project_id: int,
    user_email: str,
    project_service: ProjectService = Depends(get_project_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
    db: Session = Depends(get_db),
):
    return await project_service.add_user_to_project(project_id, user_email, current_user, db)