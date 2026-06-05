"""Pydantic схемы для строк нагрузки."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LoadLineBase(BaseModel):
    """Базовые поля строки нагрузки."""

    code: str = Field(..., min_length=2, max_length=10,
                      description="Код элемента")
    mass: float = Field(..., description="Масса (т), может быть отрицательной")
    x: float = Field(0.0, description="Координата X (м)")
    y: float = Field(0.0, description="Координата Y (м)")
    z: float = Field(0.0, description="Координата Z (м)")


class LoadLineCreate(LoadLineBase):
    """Создание строки нагрузки."""
    pass


class LoadLineUpdate(BaseModel):
    """Обновление строки нагрузки."""

    code: Optional[str] = None
    mass: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


class LoadLineResponse(LoadLineBase):
    """Ответ с данными строки нагрузки."""

    id: int
    ecr_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CenterOfGravityResponse(BaseModel):
    """Центр тяжести заявки."""

    total_mass: float
    xg: float
    yg: float
    zg: float
    mx: float
    my: float
    mz: float
