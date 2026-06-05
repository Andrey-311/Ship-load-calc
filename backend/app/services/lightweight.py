"""Сервис расчёта водоизмещения порожнем (Lightweight)."""

from typing import Dict
from dataclasses import dataclass

from app.services.aggregation import AggregatedNode


@dataclass
class LightweightResult:
    """Результат расчёта Lightweight."""

    total_mass: float
    xg: float  # Центр тяжести по X
    yg: float  # Центр тяжести по Y
    zg: float  # Центр тяжести по Z
    mx: float  # Суммарный статический момент по X
    my: float  # Суммарный статический момент по Y
    mz: float  # Суммарный статический момент по Z
    by_section: Dict[str, float]  # Масса по разделам


class LightweightCalculator:
    """Калькулятор водоизмещения порожнем.

    Согласно п. 3.7 ОСТ5Р.0206-2002, Lightweight включает разделы:
    01, 02, 03, 04, 05, 07, 09, 10, 11, 12, 13
    """

    # Список разделов, входящих в Lightweight
    LIGHTWEIGHT_SECTIONS = ["01", "02", "03", "04",
                            "05", "07", "09", "10", "11", "12", "13"]

    def __init__(self, code_hierarchy: Dict[str, Dict[str, str]]):
        """Инициализация калькулятора.

        Args:
            code_hierarchy: Словарь с информацией о кодах.
        """
        self.code_hierarchy = code_hierarchy

    def _is_lightweight_section(self, code: str) -> bool:
        """Проверить, входит ли код в Lightweight."""
        # Берём первые 2 цифры кода (раздел)
        section = code[:2]
        return section in self.LIGHTWEIGHT_SECTIONS

    def _extract_section_mass(self, tree: Dict[str, AggregatedNode]) -> Dict[str, float]:
        """Извлечь массу по разделам из агрегированного дерева."""
        result = {}
        for section in self.LIGHTWEIGHT_SECTIONS:
            if section in tree:
                result[section] = tree[section].mass
            else:
                result[section] = 0.0
        return result

    def calculate(self, aggregated_tree: Dict[str, AggregatedNode]) -> LightweightResult:
        """Рассчитать Lightweight на основе агрегированного дерева.

        Args:
            aggregated_tree: Дерево агрегированных узлов (результат LoadAggregator)

        Returns:
            LightweightResult с итоговыми значениями
        """
        total_mass = 0.0
        total_mx = 0.0
        total_my = 0.0
        total_mz = 0.0

        # Суммируем только разделы, входящие в Lightweight
        for section in self.LIGHTWEIGHT_SECTIONS:
            if section in aggregated_tree:
                node = aggregated_tree[section]
                total_mass += node.mass
                total_mx += node.mx
                total_my += node.my
                total_mz += node.mz

        # Проверка на отрицательное водоизмещение
        if total_mass < 0:
            raise ValueError(
                f"Lightweight не может быть отрицательным. Получено значение: {total_mass}. "
                "Проверьте заявки с отрицательной массой."
            )

        xg = total_mx / total_mass if total_mass != 0 else 0.0
        yg = total_my / total_mass if total_mass != 0 else 0.0
        zg = total_mz / total_mass if total_mass != 0 else 0.0

        return LightweightResult(
            total_mass=total_mass,
            xg=xg,
            yg=yg,
            zg=zg,
            mx=total_mx,
            my=total_my,
            mz=total_mz,
            by_section=self._extract_section_mass(aggregated_tree)
        )
