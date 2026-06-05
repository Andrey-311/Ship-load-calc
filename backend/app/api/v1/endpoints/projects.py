"""Эндпоинты для работы с проектами."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.repositories.unit_of_work import UnitOfWork

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    """Получить список всех проектов."""
    uow = UnitOfWork(db)
    projects = uow.projects.get_all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Получить проект по ID."""
    uow = UnitOfWork(db)
    project = uow.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """Создать новый проект."""
    uow = UnitOfWork(db)
    project = Project(**project_data.model_dump())
    result = uow.projects.create(project)
    uow.commit()
    return result


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_data: ProjectUpdate, db: Session = Depends(get_db)):
    """Обновить проект."""
    uow = UnitOfWork(db)
    project = uow.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = {k: v for k, v in project_data.model_dump().items()
                   if v is not None}
    result = uow.projects.update(project_id, **update_data)
    uow.commit()
    return result


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Удалить проект."""
    uow = UnitOfWork(db)
    project = uow.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    uow.projects.delete(project_id)
    uow.commit()
    return None
