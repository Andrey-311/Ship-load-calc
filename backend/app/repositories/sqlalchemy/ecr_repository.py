"""SQLAlchemy реализация репозитория заявок (асинхронная)."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.ecr import ECR
from app.repositories.interfaces import IECRRepository


class SQLAlchemyECRRepository(IECRRepository):
    """Репозиторий заявок на SQLAlchemy (асинхронный)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, ecr: ECR) -> ECR:
        self.session.add(ecr)
        await self.session.flush()
        await self.session.refresh(ecr)
        return ecr

    async def get_by_id(self, ecr_id: int) -> Optional[ECR]:
        result = await self.session.execute(
            select(ECR).where(ECR.id == ecr_id)
        )
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: int,
        status: Optional[str] = None
    ) -> List[ECR]:
        query = select(ECR).where(ECR.project_id == project_id)
        if status:
            query = query.where(ECR.status == status)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_status(
        self,
        ecr_id: int,
        status: str,
        approved_by_id: Optional[int] = None,
        rejection_reason: Optional[str] = None
    ) -> Optional[ECR]:
        update_data = {"status": status}
        if status == "approved":
            update_data["approved_at"] = datetime.utcnow()
            if approved_by_id:
                update_data["approved_by_id"] = approved_by_id
        if status == "rejected" and rejection_reason:
            update_data["rejection_reason"] = rejection_reason

        await self.session.execute(
            update(ECR)
            .where(ECR.id == ecr_id)
            .values(**update_data)
        )
        await self.session.flush()
        return await self.get_by_id(ecr_id)
