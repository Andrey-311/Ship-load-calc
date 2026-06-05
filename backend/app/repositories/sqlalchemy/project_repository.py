"""SQLAlchemy реализация репозитория проектов."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.interfaces import IProjectRepository


class SQLAlchemyProjectRepository(IProjectRepository):
    """Репозиторий проектов на SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        self.session.flush()
        return project

    async def get_by_id(self, project_id: int) -> Optional[Project]:
        return self.session.query(Project).filter(Project.id == project_id).first()

    async def get_all(self) -> List[Project]:
        return self.session.query(Project).all()

    async def update(self, project_id: int, **kwargs) -> Optional[Project]:
        project = await self.get_by_id(project_id)
        if project:
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            self.session.flush()
        return project

    async def delete(self, project_id: int) -> bool:
        project = await self.get_by_id(project_id)
        if project:
            self.session.delete(project)
            self.session.flush()
            return True
        return False
