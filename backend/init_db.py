"""Временный скрипт для создания БД."""

import sys
from pathlib import Path

# Добавляем backend в путь
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base
from app.core.config import BASE_DIR

# Импортируем все модели
from app.models.project import Project  # noqa
from app.models.code_directory import CodeDirectory  # noqa
from app.models.ecr import ECR  # noqa
from app.models.load_line import LoadLine  # noqa
from app.models.load_case_template import LoadCaseTemplate  # noqa

if __name__ == "__main__":
    print(f"Creating database at: {BASE_DIR / 'data' / 'ship_load.db'}")
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done!")