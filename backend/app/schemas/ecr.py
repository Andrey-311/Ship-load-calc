"""Pydantic схемы для заявок (ECR)."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ECRBase(BaseModel):
    """Базовые поля заявки."""

    comment: Optional[str] = Field(
        None, max_length=500, description="Комментарий")


class ECRCreate(ECRBase):
    """Создание заявки."""
    pass


class ECRStatusUpdate(BaseModel):
    """Обновление статуса заявки."""

    status: str = Field(..., description="draft|review|approved|rejected")
    rejection_reason: Optional[str] = Field(
        None, max_length=500, description="Причина отклонения")


class ECRResponse(ECRBase):
    """Ответ с данными заявки."""

    id: int
    project_id: int
    author_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    status: str
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ECROnlyResponse(BaseModel):
    """Упрощённый ответ для списка заявок."""

    id: int
    status: str
    comment: Optional[str]
    created_at: datetime
    total_mass: float = 0.0
    total_lines: int = 0

    class Config:
        from_attributes = True
