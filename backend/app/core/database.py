"""Database connection and session management (асинхронная версия с aiosqlite)."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import declarative_base

from .config import settings

# Асинхронный engine с aiosqlite
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Импортируем все модели, чтобы Alembic их видел
from app.models.project import Project  # noqa
from app.models.code_directory import CodeDirectory  # noqa
from app.models.ecr import ECR  # noqa
from app.models.load_line import LoadLine  # noqa
from app.models.load_case_template import LoadCaseTemplate  # noqa


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session."""
    async with AsyncSessionLocal() as session:
        yield session
