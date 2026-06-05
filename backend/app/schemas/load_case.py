"""Pydantic схемы для типовых случаев нагрузки."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoadCaseTemplateBase(BaseModel):
    """Базовые поля типового случая."""

    name: str = Field(..., max_length=100, description="Название")
    pct_08: int = Field(0, ge=0, le=200, description="Процент для раздела 08")
    pct_14: int = Field(0, ge=0, le=200, description="Процент для раздела 14")
    pct_15: int = Field(0, ge=0, le=200, description="Процент для раздела 15")
    pct_16: int = Field(0, ge=0, le=200, description="Процент для раздела 16")
    pct_17: int = Field(0, ge=0, le=200, description="Процент для раздела 17")
    pct_18: int = Field(0, ge=0, le=200, description="Процент для раздела 18")


class LoadCaseTemplateCreate(LoadCaseTemplateBase):
    """Создание типового случая."""
    pass


class LoadCaseTemplateUpdate(BaseModel):
    """Обновление типового случая."""

    name: Optional[str] = None
    pct_08: Optional[int] = None
    pct_14: Optional[int] = None
    pct_15: Optional[int] = None
    pct_16: Optional[int] = None
    pct_17: Optional[int] = None
    pct_18: Optional[int] = None


class LoadCaseTemplateResponse(LoadCaseTemplateBase):
    """Ответ с данными типового случая."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True
