"""Эндпоинты для работы с заявками (ECR)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.ecr import ECR
from app.models.load_line import LoadLine
from app.schemas.ecr import ECRCreate, ECRStatusUpdate, ECRResponse, ECROnlyResponse
from app.schemas.load_line import LoadLineResponse, LoadLineCreate, LoadLineUpdate, CenterOfGravityResponse
from app.repositories.unit_of_work import UnitOfWork

router = APIRouter(prefix="/projects/{project_id}/ecr", tags=["ecr"])


@router.get("/", response_model=List[ECROnlyResponse])
async def get_ecr_list(
    project_id: int,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Получить список заявок проекта."""
    uow = UnitOfWork(db)
    ecrs = await uow.ecrs.get_by_project(project_id, status=status_filter)

    result = []
    for ecr in ecrs:
        lines = await uow.lines.get_by_ecr(ecr.id)
        total_mass = sum(l.mass for l in lines)
        result.append({
            "id": ecr.id,
            "status": ecr.status,
            "comment": ecr.comment,
            "created_at": ecr.created_at,
            "total_mass": total_mass,
            "total_lines": len(lines)
        })
    return result


@router.post("/", response_model=ECRResponse, status_code=status.HTTP_201_CREATED)
async def create_ecr(
    project_id: int,
    ecr_data: ECRCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новую заявку."""
    uow = UnitOfWork(db)

    project = await uow.projects.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ecr = ECR(project_id=project_id, comment=ecr_data.comment)
    result = await uow.ecrs.create(ecr)
    await uow.commit()
    return result


@router.get("/{ecr_id}", response_model=ECRResponse)
async def get_ecr(
    project_id: int,
    ecr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить заявку по ID."""
    uow = UnitOfWork(db)
    ecr = await uow.ecrs.get_by_id(ecr_id)
    if not ecr or ecr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ECR not found")
    return ecr


@router.patch("/{ecr_id}/status", response_model=ECRResponse)
async def update_ecr_status(
    project_id: int,
    ecr_id: int,
    status_data: ECRStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить статус заявки."""
    uow = UnitOfWork(db)

    ecr = await uow.ecrs.get_by_id(ecr_id)
    if not ecr or ecr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ECR not found")

    result = await uow.ecrs.update_status(
        ecr_id,
        status_data.status,
        rejection_reason=status_data.rejection_reason
    )
    await uow.commit()
    return result


@router.get("/{ecr_id}/lines", response_model=List[LoadLineResponse])
async def get_ecr_lines(
    project_id: int,
    ecr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить все строки заявки."""
    uow = UnitOfWork(db)

    ecr = await uow.ecrs.get_by_id(ecr_id)
    if not ecr or ecr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ECR not found")

    lines = await uow.lines.get_by_ecr(ecr_id)
    return lines


@router.post("/{ecr_id}/lines", response_model=LoadLineResponse, status_code=status.HTTP_201_CREATED)
async def create_load_line(
    project_id: int,
    ecr_id: int,
    line_data: LoadLineCreate,
    db: AsyncSession = Depends(get_db)
):
    """Добавить строку нагрузки в заявку."""
    uow = UnitOfWork(db)

    ecr = await uow.ecrs.get_by_id(ecr_id)
    if not ecr or ecr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ECR not found")

    code = await uow.codes.get_by_code(line_data.code)
    if not code:
        raise HTTPException(
            status_code=400, detail=f"Code {line_data.code} not found")

    load_line = LoadLine(ecr_id=ecr_id, **line_data.model_dump())
    result = await uow.lines.create(load_line)
    await uow.commit()
    return result


@router.put("/lines/{line_id}", response_model=LoadLineResponse)
async def update_load_line(
    project_id: int,
    ecr_id: int,
    line_id: int,
    line_data: LoadLineUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить строку нагрузки."""
    uow = UnitOfWork(db)

    ecr = await uow.ecrs.get_by_id(ecr_id)
    if not ecr or ecr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ECR not found")

    line = await uow.lines.get_by_id(line_id)
    if not line or line.ecr_id != ecr_id:
        raise HTTPException(status_code=404, detail="Load line not found")

    update_data = {k: v for k, v in line_data.model_dump().items()
                   if v is not None}
    result = await uow.lines.update(line_id, **update_data)
    await uow.commit()
    return result


@router.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_load_line(
    project_id: int,
    ecr_id: int,
    line_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить строку нагрузки."""
    uow = UnitOfWork(db)

    ecr = await uow.ecrs.get_by_id(ecr_id)
    if not ecr or ecr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ECR not found")

    line = await uow.lines.get_by_id(line_id)
    if not line or line.ecr_id != ecr_id:
        raise HTTPException(status_code=404, detail="Load line not found")

    await uow.lines.delete(line_id)
    await uow.commit()
    return None


@router.get("/{ecr_id}/center-of-gravity", response_model=CenterOfGravityResponse)
async def get_ecr_center_of_gravity(
    project_id: int,
    ecr_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Рассчитать центр тяжести заявки."""
    uow = UnitOfWork(db)

    ecr = await uow.ecrs.get_by_id(ecr_id)
    if not ecr or ecr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ECR not found")

    lines = await uow.lines.get_by_ecr(ecr_id)

    total_mass = sum(l.mass for l in lines)
    total_mx = sum(l.mass * l.x for l in lines)
    total_my = sum(l.mass * l.y for l in lines)
    total_mz = sum(l.mass * l.z for l in lines)

    if total_mass == 0:
        return CenterOfGravityResponse(
            total_mass=0, xg=0, yg=0, zg=0, mx=0, my=0, mz=0
        )

    return CenterOfGravityResponse(
        total_mass=total_mass,
        xg=total_mx / total_mass,
        yg=total_my / total_mass,
        zg=total_mz / total_mass,
        mx=total_mx,
        my=total_my,
        mz=total_mz
    )
