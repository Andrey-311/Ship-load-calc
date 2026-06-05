"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.core.config import settings

# Создаём все таблицы при запуске (временное решение)
# Миграции настроим позже
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ship Load Calculator API",
    description="Расчёт нагрузки масс судов по ОСТ5Р.0206-2002",
    version="1.0.0",
)

# CORS для GUI клиентов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    """Проверка работоспособности сервера."""
    return {"status": "ok"}