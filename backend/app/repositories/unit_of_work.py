"""Unit of Work для управления транзакциями (асинхронная версия)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.sqlalchemy.project_repository import SQLAlchemyProjectRepository
from app.repositories.sqlalchemy.ecr_repository import SQLAlchemyECRRepository
from app.repositories.sqlalchemy.load_line_repository import SQLAlchemyLoadLineRepository
from app.repositories.sqlalchemy.code_repository import SQLAlchemyCodeRepository
from app.repositories.sqlalchemy.load_case_template_repository import SQLAlchemyLoadCaseTemplateRepository


class UnitOfWork:
    """Объединяет репозитории в одну транзакцию."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.projects = SQLAlchemyProjectRepository(session)
        self.ecrs = SQLAlchemyECRRepository(session)
        self.lines = SQLAlchemyLoadLineRepository(session)
        self.codes = SQLAlchemyCodeRepository(session)
        self.templates = SQLAlchemyLoadCaseTemplateRepository(session)

    async def commit(self):
        """Зафиксировать транзакцию."""
        await self.session.commit()

    async def rollback(self):
        """Откатить транзакцию."""
        await self.session.rollback()

    async def flush(self):
        """Сбросить изменения в БД без коммита."""
        await self.session.flush()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
