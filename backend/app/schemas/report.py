"""Pydantic схемы для отчётов и расчётов."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SectionSummary(BaseModel):
    """Сводка по разделу."""

    code: str
    name: str
    mass: float
    xg: float
    yg: float
    zg: float
    mx: float
    my: float
    mz: float


class LightweightReport(BaseModel):
    """Отчёт по Lightweight."""

    total_mass: float = Field(..., description="Водоизмещение порожнем (т)")
    xg: float = Field(..., description="Центр тяжести по X (м)")
    yg: float = Field(..., description="Центр тяжести по Y (м)")
    zg: float = Field(..., description="Центр тяжести по Z (м)")
    by_section: Dict[str, float] = Field(..., description="Масса по разделам")


class DeadweightReport(BaseModel):
    """Отчёт по Deadweight."""

    total_mass: float = Field(..., description="Дедвейт (т)")
    xg: float
    yg: float
    zg: float
    by_section: Dict[str, float]
    percentages_used: Dict[str, int]


class TotalDisplacementReport(BaseModel):
    """Отчёт по полному водоизмещению."""

    lightweight: float
    deadweight: float
    total_mass: float
    xg: float
    yg: float
    zg: float
    volume: Optional[float] = Field(
        None, description="Объёмное водоизмещение (м³)")


class AggregatedNodeResponse(BaseModel):
    """Агрегированный узел для дерева."""

    code: str
    name: str
    level: int
    mass: float
    xg: float
    yg: float
    zg: float
    children: List['AggregatedNodeResponse'] = []

    class Config:
        from_attributes = True


# Для рекурсивных ссылок
AggregatedNodeResponse.model_rebuild()
