"""Database connection and session management (синхронная версия)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import settings

# Синхронный engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
)

SessionLocal = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

# Импортируем все модели, чтобы Alembic их видел
from app.models.project import Project  # noqa
from app.models.code_directory import CodeDirectory  # noqa
from app.models.ecr import ECR  # noqa
from app.models.load_line import LoadLine  # noqa
from app.models.load_case_template import LoadCaseTemplate  # noqa


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()