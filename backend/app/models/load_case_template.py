"""LoadCaseTemplate model - типовой случай нагрузки (проценты по разделам)."""

from datetime import datetime

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LoadCaseTemplate(Base):
    """Типовой случай нагрузки (проценты для разделов 08,14,15,16,17,18)."""

    __tablename__ = "load_case_template"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Проценты для разделов (0-200, могут быть >100 для перегруза)
    pct_08: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pct_14: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pct_15: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pct_16: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pct_17: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pct_18: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<LoadCaseTemplate(id={self.id}, name={self.name})>"