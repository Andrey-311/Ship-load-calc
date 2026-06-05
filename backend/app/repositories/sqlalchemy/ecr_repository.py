"""SQLAlchemy реализация репозитория заявок."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.ecr import ECR
from app.repositories.interfaces import IECRRepository


class SQLAlchemyECRRepository(IECRRepository):
    """Репозиторий заявок на SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, ecr: ECR) -> ECR:
        self.session.add(ecr)
        self.session.flush()
        return ecr

    async def get_by_id(self, ecr_id: int) -> Optional[ECR]:
        return self.session.query(ECR).filter(ECR.id == ecr_id).first()

    async def get_by_project(
        self,
        project_id: int,
        status: Optional[str] = None
    ) -> List[ECR]:
        query = self.session.query(ECR).filter(ECR.project_id == project_id)
        if status:
            query = query.filter(ECR.status == status)
        return query.all()

    async def update_status(
        self,
        ecr_id: int,
        status: str,
        approved_by_id: Optional[int] = None,
        rejection_reason: Optional[str] = None
    ) -> Optional[ECR]:
        ecr = await self.get_by_id(ecr_id)
        if ecr:
            ecr.status = status
            if status == "approved":
                ecr.approved_at = datetime.utcnow()
                ecr.approved_by_id = approved_by_id
            if status == "rejected" and rejection_reason:
                ecr.rejection_reason = rejection_reason
            self.session.flush()
        return ecr
