"""Dependency Injection для FastAPI."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositories.unit_of_work import UnitOfWork


def get_db():
    """Получить сессию БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_uow(db: Session = Depends(get_db)):
    """Получить Unit of Work."""
    return UnitOfWork(db)
