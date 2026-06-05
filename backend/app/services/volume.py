"""Сервис расчёта объёмного водоизмещения."""

from dataclasses import dataclass


@dataclass
class VolumeDisplacementResult:
    """Результат расчёта объёмного водоизмещения."""

    volume: float  # м³
    total_mass: float  # т
    water_density: float  # т/м³


class VolumeDisplacementCalculator:
    """Калькулятор объёмного водоизмещения.

    V = D / ρ
    где D — полная масса судна (т), ρ — плотность воды (т/м³)
    """

    def calculate(self, total_mass: float, water_density: float) -> VolumeDisplacementResult:
        """Рассчитать объёмное водоизмещение.

        Args:
            total_mass: Полная масса судна (Lightweight + Deadweight) в тоннах
            water_density: Плотность воды (1.0 для пресной, 1.025 для морской)

        Returns:
            VolumeDisplacementResult с объёмом
        """
        if water_density <= 0:
            raise ValueError(
                f"Плотность воды должна быть положительной. Получено: {water_density}")

        volume = total_mass / water_density

        return VolumeDisplacementResult(
            volume=volume,
            total_mass=total_mass,
            water_density=water_density
        )
