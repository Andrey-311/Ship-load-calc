"""Pydantic схемы для проектов."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Базовые поля проекта."""

    name: str = Field(..., max_length=200, description="Название проекта")
    ship_type: Optional[str] = Field(
        None, max_length=100, description="Тип судна")
    project_type: str = Field(
        "working", description="Тип проекта: sketch|technical|working|techno_working")
    water_density: float = Field(
        1.0, description="Плотность воды (1.0 - пресная, 1.025 - морская)")
    x_min: float = Field(-100.0, description="Минимальная X (корма)")
    x_max: float = Field(100.0, description="Максимальная X (нос)")
    y_min: float = Field(-50.0, description="Минимальная Y (левый борт)")
    y_max: float = Field(50.0, description="Максимальная Y (правый борт)")
    z_max: float = Field(50.0, description="Максимальная высота от ОП")

    # Запасы
    reserve_manual_mode: bool = Field(
        False, description="Ручной режим запасов")
    reserve_percent: Optional[float] = Field(
        1.5, description="Процент запаса (авто-режим)")
    reserve_mass: Optional[float] = Field(
        None, description="Масса запаса (ручной режим)")
    reserve_stability_increment: Optional[float] = Field(
        None, description="Прибавка к Zg (ручной режим)")


class ProjectCreate(ProjectBase):
    """Создание проекта."""
    pass


class ProjectUpdate(BaseModel):
    """Обновление проекта."""

    name: Optional[str] = None
    ship_type: Optional[str] = None
    project_type: Optional[str] = None
    water_density: Optional[float] = None
    x_min: Optional[float] = None
    x_max: Optional[float] = None
    y_min: Optional[float] = None
    y_max: Optional[float] = None
    z_max: Optional[float] = None
    reserve_manual_mode: Optional[bool] = None
    reserve_percent: Optional[float] = None
    reserve_mass: Optional[float] = None
    reserve_stability_increment: Optional[float] = None


class ProjectResponse(ProjectBase):
    """Ответ с данными проекта."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
