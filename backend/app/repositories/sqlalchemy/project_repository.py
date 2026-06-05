"""SQLAlchemy реализация репозитория проектов (асинхронная)."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.models.project import Project
from app.repositories.interfaces import IProjectRepository


class SQLAlchemyProjectRepository(IProjectRepository):
    """Репозиторий проектов на SQLAlchemy (асинхронный)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def get_by_id(self, project_id: int) -> Optional[Project]:
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Project]:
        result = await self.session.execute(select(Project))
        return result.scalars().all()

    async def update(self, project_id: int, **kwargs) -> Optional[Project]:
        await self.session.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(project_id)

    async def delete(self, project_id: int) -> bool:
        result = await self.session.execute(
            delete(Project).where(Project.id == project_id)
        )
        await self.session.flush()
        return result.rowcount > 0
