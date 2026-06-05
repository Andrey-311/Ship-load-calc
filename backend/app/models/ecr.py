"""ECR model - заявка на изменение нагрузки масс."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ECR(Base):
    """Заявка (Engineering Change Request)."""

    __tablename__ = "ecr"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Временно убираем внешние ключи на users
    author_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # без ForeignKey
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # без ForeignKey
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        comment="draft|review|approved|rejected"
    )
    comment: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<ECR(id={self.id}, project_id={self.project_id}, status={self.status})>"