"""Эндпоинты для отчётов и расчётов нагрузки масс."""

from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.unit_of_work import UnitOfWork
from app.services.ship_load_service import ShipLoadService
from app.schemas.report import (
    LightweightReport,
    DeadweightReport,
    TotalDisplacementReport,
    AggregatedNodeResponse
)

router = APIRouter(prefix="/projects/{project_id}/reports", tags=["reports"])


async def get_ship_load_service(db: AsyncSession = Depends(get_db)) -> ShipLoadService:
    """Dependency для получения ShipLoadService."""
    uow = UnitOfWork(db)
    return ShipLoadService(uow)


@router.get("/lightweight", response_model=LightweightReport)
async def get_lightweight(
    project_id: int,
    service: ShipLoadService = Depends(get_ship_load_service)
):
    """Рассчитать водоизмещение порожнем (Lightweight)."""
    try:
        result = await service.calculate_lightweight(project_id)
        return LightweightReport(
            total_mass=result.total_mass,
            xg=result.xg,
            yg=result.yg,
            zg=result.zg,
            by_section=result.by_section
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deadweight", response_model=DeadweightReport)
async def get_deadweight(
    project_id: int,
    pct_08: int = Query(100, ge=0, le=200,
                        description="Процент для раздела 08"),
    pct_14: int = Query(100, ge=0, le=200,
                        description="Процент для раздела 14"),
    pct_15: int = Query(100, ge=0, le=200,
                        description="Процент для раздела 15"),
    pct_16: int = Query(100, ge=0, le=200,
                        description="Процент для раздела 16"),
    pct_17: int = Query(0, ge=0, le=200, description="Процент для раздела 17"),
    pct_18: int = Query(0, ge=0, le=200, description="Процент для раздела 18"),
    load_case_id: int = Query(
        None, description="ID типового случая (переопределяет проценты)"),
    db: AsyncSession = Depends(get_db),
    service: ShipLoadService = Depends(get_ship_load_service)
):
    """Рассчитать дедвейт (Deadweight) с заданными процентами.

    Если указан load_case_id, проценты берутся из типового случая.
    """
    try:
        # Если указан типовой случай, получаем проценты из него
        if load_case_id:
            uow = UnitOfWork(db)
            template = await uow.templates.get_by_id(load_case_id)
            if not template:
                raise HTTPException(
                    status_code=404, detail="Load case template not found")
            percentages = {
                "08": template.pct_08,
                "14": template.pct_14,
                "15": template.pct_15,
                "16": template.pct_16,
                "17": template.pct_17,
                "18": template.pct_18,
            }
        else:
            percentages = {
                "08": pct_08,
                "14": pct_14,
                "15": pct_15,
                "16": pct_16,
                "17": pct_17,
                "18": pct_18,
            }

        result = await service.calculate_deadweight(project_id, percentages)

        return DeadweightReport(
            total_mass=result.total_mass,
            xg=result.xg,
            yg=result.yg,
            zg=result.zg,
            by_section=result.by_section,
            percentages_used=percentages
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/total-displacement", response_model=TotalDisplacementReport)
async def get_total_displacement(
    project_id: int,
    pct_08: int = Query(100, ge=0, le=200),
    pct_14: int = Query(100, ge=0, le=200),
    pct_15: int = Query(100, ge=0, le=200),
    pct_16: int = Query(100, ge=0, le=200),
    pct_17: int = Query(0, ge=0, le=200),
    pct_18: int = Query(0, ge=0, le=200),
    include_volume: bool = Query(
        False, description="Включить объёмное водоизмещение"),
    db: AsyncSession = Depends(get_db),
    service: ShipLoadService = Depends(get_ship_load_service)
):
    """Рассчитать полное водоизмещение (Lightweight + Deadweight)."""
    try:
        percentages = {
            "08": pct_08,
            "14": pct_14,
            "15": pct_15,
            "16": pct_16,
            "17": pct_17,
            "18": pct_18,
        }

        lightweight = await service.calculate_lightweight(project_id)
        deadweight = await service.calculate_deadweight(project_id, percentages)

        total_mass = lightweight.total_mass + deadweight.total_mass

        # Рассчитываем общий центр тяжести
        total_mx = lightweight.mx + deadweight.mx
        total_my = lightweight.my + deadweight.my
        total_mz = lightweight.mz + deadweight.mz

        xg = total_mx / total_mass if total_mass != 0 else 0.0
        yg = total_my / total_mass if total_mass != 0 else 0.0
        zg = total_mz / total_mass if total_mass != 0 else 0.0

        result = TotalDisplacementReport(
            lightweight=lightweight.total_mass,
            deadweight=deadweight.total_mass,
            total_mass=total_mass,
            xg=xg,
            yg=yg,
            zg=zg,
            volume=None
        )

        if include_volume:
            # Получаем плотность воды из проекта
            uow = UnitOfWork(db)
            project = await uow.projects.get_by_id(project_id)
            if project:
                volume_result = await service.calculate_volume_displacement(
                    project_id, percentages, project.water_density
                )
                result.volume = volume_result.volume

        return result
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aggregated-tree", response_model=Dict[str, AggregatedNodeResponse])
async def get_aggregated_tree(
    project_id: int,
    service: ShipLoadService = Depends(get_ship_load_service)
):
    """Получить агрегированное дерево нагрузки."""
    try:
        tree = await service.get_aggregated_tree(project_id)

        # Конвертируем в response model
        def convert_node(node):
            return AggregatedNodeResponse(
                code=node.code,
                name=node.name,
                level=node.level,
                mass=node.mass,
                xg=node.xg,
                yg=node.yg,
                zg=node.zg,
                children=[convert_node(child)
                          for child in node.children.values()]
            )

        return {code: convert_node(node) for code, node in tree.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
