"""Эндпоинты для работы с типовыми случаями нагрузки."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.load_case_template import LoadCaseTemplate
from app.repositories.unit_of_work import UnitOfWork
from app.schemas.load_case import (
    LoadCaseTemplateCreate,
    LoadCaseTemplateUpdate,
    LoadCaseTemplateResponse
)

router = APIRouter(prefix="/load-cases", tags=["load-cases"])


@router.get("/", response_model=List[LoadCaseTemplateResponse])
def get_all_templates(db: Session = Depends(get_db)):
    """Получить все типовые случаи нагрузки."""
    uow = UnitOfWork(db)
    templates = uow.templates.get_all()
    return templates


@router.get("/{template_id}", response_model=LoadCaseTemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Получить типовой случай по ID."""
    uow = UnitOfWork(db)
    template = uow.templates.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/", response_model=LoadCaseTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(template_data: LoadCaseTemplateCreate, db: Session = Depends(get_db)):
    """Создать новый типовой случай нагрузки."""
    uow = UnitOfWork(db)

    # Проверяем уникальность имени
    existing = uow.templates.get_by_name(template_data.name)
    if existing:
        raise HTTPException(
            status_code=400, detail="Template with this name already exists")

    template = LoadCaseTemplate(**template_data.model_dump())
    result = uow.templates.create(template)
    uow.commit()
    return result


@router.put("/{template_id}", response_model=LoadCaseTemplateResponse)
def update_template(
    template_id: int,
    template_data: LoadCaseTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Обновить типовой случай нагрузки."""
    uow = UnitOfWork(db)

    template = uow.templates.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = {k: v for k, v in template_data.model_dump().items()
                   if v is not None}
    result = uow.templates.update(template_id, **update_data)
    uow.commit()
    return result


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Удалить типовой случай нагрузки."""
    uow = UnitOfWork(db)

    template = uow.templates.get_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    uow.templates.delete(template_id)
    uow.commit()
    return None
