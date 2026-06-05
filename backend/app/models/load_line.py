"""LoadLine model - строка нагрузки масс."""

from datetime import datetime

from sqlalchemy import Float, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LoadLine(Base):
    """Строка нагрузки масс (принадлежит заявке)."""

    __tablename__ = "load_line"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ecr_id: Mapped[int] = mapped_column(ForeignKey("ecr.id", ondelete="CASCADE"), nullable=False, index=True)

    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    mass: Mapped[float] = mapped_column(Float, nullable=False)
    x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    z: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<LoadLine(id={self.id}, ecr_id={self.ecr_id}, code={self.code}, mass={self.mass})>"