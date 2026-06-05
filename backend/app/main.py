"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.core.config import settings
from app.api.v1.endpoints import projects, ecr, reports, codes, load_cases


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title="Ship Load Calculator API",
    description="Расчёт нагрузки масс судов по ОСТ5Р.0206-2002",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS для GUI клиентов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация эндпоинтов
app.include_router(projects.router, prefix="/api/v1")
app.include_router(ecr.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(codes.router, prefix="/api/v1")
app.include_router(load_cases.router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    """Проверка работоспособности сервера."""
    return {"status": "ok"}


@app.get("/")
async def root() -> dict:
    """Корневой эндпоинт."""
    return {
        "message": "Ship Load Calculator API",
        "version": "1.0.0",
        "docs": "/docs"
    }
