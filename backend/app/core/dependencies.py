"""Dependency Injection для FastAPI."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.unit_of_work import UnitOfWork


async def get_uow(
    db: AsyncSession = Depends(get_db)
) -> UnitOfWork:
    """Получить Unit of Work."""
    return UnitOfWork(db)
