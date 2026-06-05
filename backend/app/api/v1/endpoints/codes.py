"""Эндпоинты для работы со справочником кодов."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.code_directory import CodeDirectory
from app.repositories.unit_of_work import UnitOfWork
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/codes", tags=["codes"])


@router.get("/", response_model=List[dict])
async def get_all_codes(db: AsyncSession = Depends(get_db)):
    """Получить весь справочник кодов."""
    uow = UnitOfWork(db)
    codes = await uow.codes.get_all()
    return [
        {
            "code": c.code,
            "name": c.name,
            "level": c.level,
            "parent_code": c.parent_code
        }
        for c in codes
    ]


@router.get("/{code}", response_model=dict)
async def get_code(code: str, db: AsyncSession = Depends(get_db)):
    """Получить элемент справочника по коду."""
    uow = UnitOfWork(db)
    code_item = await uow.codes.get_by_code(code)
    if not code_item:
        raise HTTPException(status_code=404, detail=f"Code {code} not found")

    return {
        "code": code_item.code,
        "name": code_item.name,
        "level": code_item.level,
        "parent_code": code_item.parent_code
    }


@router.get("/{code}/children", response_model=List[dict])
async def get_code_children(code: str, db: AsyncSession = Depends(get_db)):
    """Получить все дочерние элементы кода."""
    uow = UnitOfWork(db)

    code_item = await uow.codes.get_by_code(code)
    if not code_item:
        raise HTTPException(status_code=404, detail=f"Code {code} not found")

    children = await uow.codes.get_children(code)
    return [
        {
            "code": c.code,
            "name": c.name,
            "level": c.level,
            "parent_code": c.parent_code
        }
        for c in children
    ]


@router.post("/import", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_codes(
    file: UploadFile = File(..., description="CSV/JSON файл со справочником"),
    db: AsyncSession = Depends(get_db)
):
    """Импортировать справочник кодов из файла."""
    import csv
    import json

    uow = UnitOfWork(db)
    content = await file.read()

    if file.filename.endswith('.csv'):
        text = content.decode('utf-8')
        reader = csv.DictReader(text.splitlines())
        count = 0
        for row in reader:
            code = row.get('code')
            if not code:
                continue

            existing = await uow.codes.get_by_code(code)
            if not existing:
                code_item = CodeDirectory(
                    code=code,
                    name=row.get('name', ''),
                    level=int(row.get('level', 0)),
                    parent_code=row.get('parent_code')
                )
                await uow.codes.create(code_item)
                count += 1
    else:
        data = json.loads(content)
        count = 0
        for item in data:
            code = item.get('code')
            if not code:
                continue

            existing = await uow.codes.get_by_code(code)
            if not existing:
                code_item = CodeDirectory(
                    code=code,
                    name=item.get('name', ''),
                    level=item.get('level', 0),
                    parent_code=item.get('parent_code')
                )
                await uow.codes.create(code_item)
                count += 1

    await uow.commit()
    return MessageResponse(message=f"Imported {count} codes")
