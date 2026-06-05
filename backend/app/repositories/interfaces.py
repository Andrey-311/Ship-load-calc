"""Абстрактные интерфейсы репозиториев."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.project import Project
from app.models.ecr import ECR
from app.models.load_line import LoadLine
from app.models.code_directory import CodeDirectory
from app.models.load_case_template import LoadCaseTemplate


class IProjectRepository(ABC):
    """Репозиторий для работы с проектами."""

    @abstractmethod
    async def create(self, project: Project) -> Project:
        """Создать новый проект."""
        pass

    @abstractmethod
    async def get_by_id(self, project_id: int) -> Optional[Project]:
        """Получить проект по ID."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Project]:
        """Получить все проекты."""
        pass

    @abstractmethod
    async def update(self, project_id: int, **kwargs) -> Optional[Project]:
        """Обновить проект."""
        pass

    @abstractmethod
    async def delete(self, project_id: int) -> bool:
        """Удалить проект."""
        pass


class IECRRepository(ABC):
    """Репозиторий для работы с заявками."""

    @abstractmethod
    async def create(self, ecr: ECR) -> ECR:
        """Создать заявку."""
        pass

    @abstractmethod
    async def get_by_id(self, ecr_id: int) -> Optional[ECR]:
        """Получить заявку по ID."""
        pass

    @abstractmethod
    async def get_by_project(
        self,
        project_id: int,
        status: Optional[str] = None
    ) -> List[ECR]:
        """Получить заявки проекта (опционально по статусу)."""
        pass

    @abstractmethod
    async def update_status(
        self,
        ecr_id: int,
        status: str,
        approved_by_id: Optional[int] = None,
        rejection_reason: Optional[str] = None
    ) -> Optional[ECR]:
        """Обновить статус заявки."""
        pass


class ILoadLineRepository(ABC):
    """Репозиторий для работы со строками нагрузки."""

    @abstractmethod
    async def create(self, load_line: LoadLine) -> LoadLine:
        """Создать строку нагрузки."""
        pass

    @abstractmethod
    async def get_by_id(self, line_id: int) -> Optional[LoadLine]:
        """Получить строку по ID."""
        pass

    @abstractmethod
    async def get_by_ecr(self, ecr_id: int) -> List[LoadLine]:
        """Получить все строки заявки."""
        pass

    @abstractmethod
    async def update(self, line_id: int, **kwargs) -> Optional[LoadLine]:
        """Обновить строку нагрузки."""
        pass

    @abstractmethod
    async def delete(self, line_id: int) -> bool:
        """Удалить строку нагрузки."""
        pass

    @abstractmethod
    async def get_by_codes_and_ecr(
        self,
        ecr_id: int,
        codes: List[str]
    ) -> List[LoadLine]:
        """Получить строки по кодам и заявке."""
        pass


class ICodeRepository(ABC):
    """Репозиторий для работы со справочником кодов."""

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[CodeDirectory]:
        """Получить элемент справочника по коду."""
        pass

    @abstractmethod
    async def get_all(self) -> List[CodeDirectory]:
        """Получить весь справочник."""
        pass

    @abstractmethod
    async def get_parent_code(self, code: str) -> Optional[str]:
        """Получить родительский код."""
        pass

    @abstractmethod
    async def get_children(self, parent_code: str) -> List[CodeDirectory]:
        """Получить все дочерние элементы."""
        pass


class ILoadCaseTemplateRepository(ABC):
    """Репозиторий для работы с типовыми случаями нагрузки."""

    @abstractmethod
    async def create(self, template: LoadCaseTemplate) -> LoadCaseTemplate:
        """Создать типовой случай."""
        pass

    @abstractmethod
    async def get_by_id(self, template_id: int) -> Optional[LoadCaseTemplate]:
        """Получить по ID."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[LoadCaseTemplate]:
        """Получить по имени."""
        pass

    @abstractmethod
    async def get_all(self) -> List[LoadCaseTemplate]:
        """Получить все типовые случаи."""
        pass

    @abstractmethod
    async def update(self, template_id: int, **kwargs) -> Optional[LoadCaseTemplate]:
        """Обновить типовой случай."""
        pass

    @abstractmethod
    async def delete(self, template_id: int) -> bool:
        """Удалить типовой случай."""
        pass
