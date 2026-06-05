"""Сервис расчёта дедвейта (Deadweight)."""

from typing import Dict
from dataclasses import dataclass

from app.services.aggregation import AggregatedNode


@dataclass
class DeadweightResult:
    """Результат расчёта Deadweight."""

    total_mass: float
    xg: float
    yg: float
    zg: float
    mx: float
    my: float
    mz: float
    by_section: Dict[str, float]  # Масса по разделам с учётом процентов


class DeadweightCalculator:
    """Калькулятор дедвейта.

    Согласно п. 3.7 ОСТ5Р.0206-2002 и Приложению А, Deadweight включает разделы:
    08, 14, 15, 16, 17, 18 с возможностью задания процентов.

    Примечание: Экипаж (раздел 14) всегда 100%, даже если провизия и вода 10%.
    """

    # Разделы, входящие в Deadweight
    DEADWEIGHT_SECTIONS = ["08", "14", "15", "16", "17", "18"]

    def __init__(self, code_hierarchy: Dict[str, Dict[str, str]]):
        """Инициализация калькулятора.

        Args:
            code_hierarchy: Словарь с информацией о кодах.
        """
        self.code_hierarchy = code_hierarchy

    def calculate(
        self,
        aggregated_tree: Dict[str, AggregatedNode],
        percentages: Dict[str, int]
    ) -> DeadweightResult:
        """Рассчитать Deadweight на основе агрегированного дерева и процентов.

        Args:
            aggregated_tree: Дерево агрегированных узлов
            percentages: Проценты для разделов в формате {"08": 100, "14": 100, ...}

        Returns:
            DeadweightResult с итоговыми значениями
        """
        total_mass = 0.0
        total_mx = 0.0
        total_my = 0.0
        total_mz = 0.0
        by_section = {}

        for section in self.DEADWEIGHT_SECTIONS:
            percent = percentages.get(section, 0)
            factor = percent / 100.0

            if section in aggregated_tree:
                node = aggregated_tree[section]
                # Экипаж (14) всегда 100% согласно Приложению А
                if section == "14":
                    factor = 1.0

                section_mass = node.mass * factor
                section_mx = node.mx * factor
                section_my = node.my * factor
                section_mz = node.mz * factor

                total_mass += section_mass
                total_mx += section_mx
                total_my += section_my
                total_mz += section_mz
                by_section[section] = section_mass
            else:
                by_section[section] = 0.0

        # Проверка на отрицательный дедвейт
        if total_mass < 0:
            raise ValueError(
                f"Deadweight не может быть отрицательным. Получено значение: {total_mass}. "
                "Проверьте проценты и заявки с отрицательной массой."
            )

        xg = total_mx / total_mass if total_mass != 0 else 0.0
        yg = total_my / total_mass if total_mass != 0 else 0.0
        zg = total_mz / total_mass if total_mass != 0 else 0.0

        return DeadweightResult(
            total_mass=total_mass,
            xg=xg,
            yg=yg,
            zg=zg,
            mx=total_mx,
            my=total_my,
            mz=total_mz,
            by_section=by_section
        )
