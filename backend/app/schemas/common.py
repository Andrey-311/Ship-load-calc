"""Общие Pydantic схемы."""

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Стандартный ответ с сообщением."""

    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    """Стандартный ответ об ошибке."""

    error: str
    detail: str | None = None
    status_code: int = 400
