"""SQLAlchemy реализация репозитория справочника кодов (асинхронная)."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.code_directory import CodeDirectory
from app.repositories.interfaces import ICodeRepository


class SQLAlchemyCodeRepository(ICodeRepository):
    """Репозиторий справочника кодов на SQLAlchemy (асинхронный)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, code_item: CodeDirectory) -> CodeDirectory:
        self.session.add(code_item)
        await self.session.flush()
        await self.session.refresh(code_item)
        return code_item

    async def get_by_code(self, code: str) -> Optional[CodeDirectory]:
        result = await self.session.execute(
            select(CodeDirectory).where(CodeDirectory.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[CodeDirectory]:
        result = await self.session.execute(select(CodeDirectory))
        return result.scalars().all()

    async def get_parent_code(self, code: str) -> Optional[str]:
        item = await self.get_by_code(code)
        return item.parent_code if item else None

    async def get_children(self, parent_code: str) -> List[CodeDirectory]:
        result = await self.session.execute(
            select(CodeDirectory).where(
                CodeDirectory.parent_code == parent_code)
        )
        return result.scalars().all()
