"""SQLAlchemy реализация репозитория строк нагрузки."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.load_line import LoadLine
from app.repositories.interfaces import ILoadLineRepository


class SQLAlchemyLoadLineRepository(ILoadLineRepository):
    """Репозиторий строк нагрузки на SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, load_line: LoadLine) -> LoadLine:
        self.session.add(load_line)
        self.session.flush()
        return load_line

    async def get_by_id(self, line_id: int) -> Optional[LoadLine]:
        return self.session.query(LoadLine).filter(LoadLine.id == line_id).first()

    async def get_by_ecr(self, ecr_id: int) -> List[LoadLine]:
        return self.session.query(LoadLine).filter(LoadLine.ecr_id == ecr_id).all()

    async def update(self, line_id: int, **kwargs) -> Optional[LoadLine]:
        line = await self.get_by_id(line_id)
        if line:
            for key, value in kwargs.items():
                if hasattr(line, key):
                    setattr(line, key, value)
            self.session.flush()
        return line

    async def delete(self, line_id: int) -> bool:
        line = await self.get_by_id(line_id)
        if line:
            self.session.delete(line)
            self.session.flush()
            return True
        return False

    async def get_by_codes_and_ecr(
        self,
        ecr_id: int,
        codes: List[str]
    ) -> List[LoadLine]:
        return self.session.query(LoadLine).filter(
            LoadLine.ecr_id == ecr_id,
            LoadLine.code.in_(codes)
        ).all()
