"""Главный фасадный сервис для расчёта нагрузки масс."""

from typing import Dict, List

from app.models.load_line import LoadLine
from app.repositories.unit_of_work import UnitOfWork
from app.services.aggregation import LoadAggregator, AggregatedNode
from app.services.lightweight import LightweightCalculator, LightweightResult
from app.services.deadweight import DeadweightCalculator, DeadweightResult
from app.services.volume import VolumeDisplacementCalculator, VolumeDisplacementResult


class ShipLoadService:
    """Главный сервис для расчёта нагрузки масс.

    Объединяет все подсервисы и предоставляет единый интерфейс.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def _get_code_hierarchy(self) -> Dict[str, Dict[str, str]]:
        """Получить иерархию кодов из БД."""
        codes = await self.uow.codes.get_all()
        return {
            code.code: {
                "name": code.name,
                "parent": code.parent_code,
                "level": code.level
            }
            for code in codes
        }

    async def _get_active_load_lines(self, project_id: int) -> List[LoadLine]:
        """Получить все строки активной нагрузки (approved ECR)."""
        ecrs = await self.uow.ecrs.get_by_project(project_id, status="approved")
        all_lines = []
        for ecr in ecrs:
            lines = await self.uow.lines.get_by_ecr(ecr.id)
            all_lines.extend(lines)
        return all_lines

    async def get_aggregated_tree(self, project_id: int) -> Dict[str, AggregatedNode]:
        """Получить агрегированное дерево нагрузки для проекта."""
        lines = await self._get_active_load_lines(project_id)
        hierarchy = await self._get_code_hierarchy()

        aggregator = LoadAggregator(hierarchy)
        line_tuples = [(line.code, line.mass, line.x, line.y, line.z)
                       for line in lines]

        return aggregator.aggregate(line_tuples)

    async def calculate_lightweight(self, project_id: int) -> LightweightResult:
        """Рассчитать Lightweight."""
        tree = await self.get_aggregated_tree(project_id)
        hierarchy = await self._get_code_hierarchy()

        calculator = LightweightCalculator(hierarchy)
        return calculator.calculate(tree)

    async def calculate_deadweight(
        self,
        project_id: int,
        percentages: Dict[str, int]
    ) -> DeadweightResult:
        """Рассчитать Deadweight с заданными процентами."""
        tree = await self.get_aggregated_tree(project_id)
        hierarchy = await self._get_code_hierarchy()

        calculator = DeadweightCalculator(hierarchy)
        return calculator.calculate(tree, percentages)

    async def calculate_total_displacement(
        self,
        project_id: int,
        percentages: Dict[str, int]
    ) -> float:
        """Рассчитать полное водоизмещение (Lightweight + Deadweight)."""
        lightweight = await self.calculate_lightweight(project_id)
        deadweight = await self.calculate_deadweight(project_id, percentages)
        return lightweight.total_mass + deadweight.total_mass

    async def calculate_volume_displacement(
        self,
        project_id: int,
        percentages: Dict[str, int],
        water_density: float
    ) -> VolumeDisplacementResult:
        """Рассчитать объёмное водоизмещение."""
        total_mass = await self.calculate_total_displacement(project_id, percentages)
        calculator = VolumeDisplacementCalculator()
        return calculator.calculate(total_mass, water_density)
