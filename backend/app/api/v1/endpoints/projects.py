"""Эндпоинты для работы с проектами."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.repositories.unit_of_work import UnitOfWork

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(db: AsyncSession = Depends(get_db)):
    """Получить список всех проектов."""
    uow = UnitOfWork(db)
    projects = await uow.projects.get_all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Получить проект по ID."""
    uow = UnitOfWork(db)
    project = await uow.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Создать новый проект."""
    uow = UnitOfWork(db)
    project = Project(**project_data.model_dump())
    result = await uow.projects.create(project)
    await uow.commit()
    return result


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить проект."""
    uow = UnitOfWork(db)
    project = await uow.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = {k: v for k, v in project_data.model_dump().items()
                   if v is not None}
    result = await uow.projects.update(project_id, **update_data)
    await uow.commit()
    return result


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить проект."""
    uow = UnitOfWork(db)
    project = await uow.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await uow.projects.delete(project_id)
    await uow.commit()
    return None
