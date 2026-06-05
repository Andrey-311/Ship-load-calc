"""Application configuration."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Корень проекта (папка, где находится backend)
BASE_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Database - используем простой относительный путь
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'ship_load.db'}"

    # Application
    environment: str = "development"
    debug: bool = True
    api_port: int = 8000

    # Auth (опционально, пока отключено)
    auth_enabled: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Создаём папку data, если её нет
data_dir = BASE_DIR / "data"
data_dir.mkdir(exist_ok=True)