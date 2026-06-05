"""SQLAlchemy реализация репозитория строк нагрузки (асинхронная)."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.load_line import LoadLine
from app.repositories.interfaces import ILoadLineRepository


class SQLAlchemyLoadLineRepository(ILoadLineRepository):
    """Репозиторий строк нагрузки на SQLAlchemy (асинхронный)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, load_line: LoadLine) -> LoadLine:
        self.session.add(load_line)
        await self.session.flush()
        await self.session.refresh(load_line)
        return load_line

    async def get_by_id(self, line_id: int) -> Optional[LoadLine]:
        result = await self.session.execute(
            select(LoadLine).where(LoadLine.id == line_id)
        )
        return result.scalar_one_or_none()

    async def get_by_ecr(self, ecr_id: int) -> List[LoadLine]:
        result = await self.session.execute(
            select(LoadLine).where(LoadLine.ecr_id == ecr_id)
        )
        return result.scalars().all()

    async def update(self, line_id: int, **kwargs) -> Optional[LoadLine]:
        await self.session.execute(
            update(LoadLine)
            .where(LoadLine.id == line_id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(line_id)

    async def delete(self, line_id: int) -> bool:
        result = await self.session.execute(
            delete(LoadLine).where(LoadLine.id == line_id)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def get_by_codes_and_ecr(
        self,
        ecr_id: int,
        codes: List[str]
    ) -> List[LoadLine]:
        result = await self.session.execute(
            select(LoadLine).where(
                LoadLine.ecr_id == ecr_id,
                LoadLine.code.in_(codes)
            )
        )
        return result.scalars().all()
