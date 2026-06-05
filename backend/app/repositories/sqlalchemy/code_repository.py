"""SQLAlchemy реализация репозитория справочника кодов."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.code_directory import CodeDirectory
from app.repositories.interfaces import ICodeRepository


class SQLAlchemyCodeRepository(ICodeRepository):
    """Репозиторий справочника кодов на SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    async def get_by_code(self, code: str) -> Optional[CodeDirectory]:
        return self.session.query(CodeDirectory).filter(
            CodeDirectory.code == code
        ).first()

    async def get_all(self) -> List[CodeDirectory]:
        return self.session.query(CodeDirectory).all()

    async def get_parent_code(self, code: str) -> Optional[str]:
        item = await self.get_by_code(code)
        return item.parent_code if item else None

    async def get_children(self, parent_code: str) -> List[CodeDirectory]:
        return self.session.query(CodeDirectory).filter(
            CodeDirectory.parent_code == parent_code
        ).all()
