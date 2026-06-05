"""Project model - судно или док, для которого ведётся расчёт."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Float, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Project(Base):
    """Проект судна (или дока, земснаряда и т.д.)."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    ship_type: Mapped[str] = mapped_column(String(100), nullable=True)
    project_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="working",
        comment="sketch|technical|working|techno_working"
    )

    # Плотность воды (1.0 - пресная, 1.025 - морская)
    water_density: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    # Габариты судна для валидации координат
    x_min: Mapped[float] = mapped_column(Float, nullable=False, default=-100.0)
    x_max: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    y_min: Mapped[float] = mapped_column(Float, nullable=False, default=-50.0)
    y_max: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)
    z_max: Mapped[float] = mapped_column(Float, nullable=False, default=50.0)

    # Режим расчёта запасов (ручной или автоматический)
    reserve_manual_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Для автоматического режима
    reserve_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=1.5)

    # Для ручного режима
    reserve_mass: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reserve_stability_increment: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name})>"