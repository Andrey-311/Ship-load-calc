"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/ship_load.db"

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
