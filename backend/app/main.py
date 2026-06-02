"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Ship Load Calculator API",
    description="Расчёт нагрузки масс судов по ОСТ5Р.0206-2002",
    version="1.0.0",
)

# CORS для GUI клиентов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшне ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict:
    """Проверка работоспособности сервера."""
    return {"status": "ok"}
