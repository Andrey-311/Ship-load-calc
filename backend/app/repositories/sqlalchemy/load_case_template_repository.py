"""SQLAlchemy реализация репозитория типовых случаев."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.load_case_template import LoadCaseTemplate
from app.repositories.interfaces import ILoadCaseTemplateRepository


class SQLAlchemyLoadCaseTemplateRepository(ILoadCaseTemplateRepository):
    """Репозиторий типовых случаев на SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    async def create(self, template: LoadCaseTemplate) -> LoadCaseTemplate:
        self.session.add(template)
        self.session.flush()
        return template

    async def get_by_id(self, template_id: int) -> Optional[LoadCaseTemplate]:
        return self.session.query(LoadCaseTemplate).filter(
            LoadCaseTemplate.id == template_id
        ).first()

    async def get_by_name(self, name: str) -> Optional[LoadCaseTemplate]:
        return self.session.query(LoadCaseTemplate).filter(
            LoadCaseTemplate.name == name
        ).first()

    async def get_all(self) -> List[LoadCaseTemplate]:
        return self.session.query(LoadCaseTemplate).all()

    async def update(self, template_id: int, **kwargs) -> Optional[LoadCaseTemplate]:
        template = await self.get_by_id(template_id)
        if template:
            for key, value in kwargs.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            self.session.flush()
        return template

    async def delete(self, template_id: int) -> bool:
        template = await self.get_by_id(template_id)
        if template:
            self.session.delete(template)
            self.session.flush()
            return True
        return False
