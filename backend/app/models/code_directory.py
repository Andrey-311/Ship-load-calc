"""CodeDirectory model - справочник 10-значных кодов из ОСТ5Р.0206-2002."""

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CodeDirectory(Base):
    """Справочник элементов нагрузки масс."""

    __tablename__ = "code_directory"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    level: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="1=раздел, 2=группа, 3=подгруппа, 4=статья, 5=подстатья"
    )
    parent_code: Mapped[str] = mapped_column(String(10), nullable=True, index=True)

    def __repr__(self) -> str:
        return f"<CodeDirectory(code={self.code}, name={self.name[:50]})>"