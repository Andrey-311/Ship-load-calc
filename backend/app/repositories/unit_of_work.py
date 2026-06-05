"""Unit of Work для управления транзакциями."""

from sqlalchemy.orm import Session

from app.repositories.sqlalchemy import (
    SQLAlchemyProjectRepository,
    SQLAlchemyECRRepository,
    SQLAlchemyLoadLineRepository,
    SQLAlchemyCodeRepository,
    SQLAlchemyLoadCaseTemplateRepository,
)


class UnitOfWork:
    """Объединяет репозитории в одну транзакцию."""

    def __init__(self, session: Session):
        self.session = session
        self.projects = SQLAlchemyProjectRepository(session)
        self.ecrs = SQLAlchemyECRRepository(session)
        self.lines = SQLAlchemyLoadLineRepository(session)
        self.codes = SQLAlchemyCodeRepository(session)
        self.templates = SQLAlchemyLoadCaseTemplateRepository(session)

    def commit(self):
        """Зафиксировать транзакцию."""
        self.session.commit()

    def rollback(self):
        """Откатить транзакцию."""
        self.session.rollback()

    def flush(self):
        """Сбросить изменения в БД без коммита."""
        self.session.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
