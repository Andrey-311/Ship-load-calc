"""SQLAlchemy реализация репозитория типовых случаев (асинхронная)."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.load_case_template import LoadCaseTemplate
from app.repositories.interfaces import ILoadCaseTemplateRepository


class SQLAlchemyLoadCaseTemplateRepository(ILoadCaseTemplateRepository):
    """Репозиторий типовых случаев на SQLAlchemy (асинхронный)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, template: LoadCaseTemplate) -> LoadCaseTemplate:
        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(template)
        return template

    async def get_by_id(self, template_id: int) -> Optional[LoadCaseTemplate]:
        result = await self.session.execute(
            select(LoadCaseTemplate).where(LoadCaseTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[LoadCaseTemplate]:
        result = await self.session.execute(
            select(LoadCaseTemplate).where(LoadCaseTemplate.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[LoadCaseTemplate]:
        result = await self.session.execute(select(LoadCaseTemplate))
        return result.scalars().all()

    async def update(self, template_id: int, **kwargs) -> Optional[LoadCaseTemplate]:
        await self.session.execute(
            update(LoadCaseTemplate)
            .where(LoadCaseTemplate.id == template_id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(template_id)

    async def delete(self, template_id: int) -> bool:
        result = await self.session.execute(
            delete(LoadCaseTemplate).where(LoadCaseTemplate.id == template_id)
        )
        await self.session.flush()
        return result.rowcount > 0
