"""Сервис агрегации нагрузки масс по иерархии кодов."""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class AggregatedNode:
    """Агрегированный узел иерархии (раздел, группа, подгруппа и т.д.)."""

    code: str
    name: str = ""
    level: int = 0
    mass: float = 0.0
    mx: float = 0.0  # Статический момент относительно X
    my: float = 0.0  # Статический момент относительно Y
    mz: float = 0.0  # Статический момент относительно Z
    children: Dict[str, 'AggregatedNode'] = field(default_factory=dict)

    @property
    def xg(self) -> float:
        """Центр тяжести по X."""
        return self.mx / self.mass if self.mass != 0 else 0.0

    @property
    def yg(self) -> float:
        """Центр тяжести по Y."""
        return self.my / self.mass if self.mass != 0 else 0.0

    @property
    def zg(self) -> float:
        """Центр тяжести по Z."""
        return self.mz / self.mass if self.mass != 0 else 0.0

    def add_line(self, code: str, mass: float, x: float, y: float, z: float):
        """Добавить строку нагрузки в узел."""
        self.mass += mass
        self.mx += mass * x
        self.my += mass * y
        self.mz += mass * z


class LoadAggregator:
    """Агрегатор нагрузки масс по иерархии кодов.

    Принимает список строк нагрузки и строит дерево по кодам.
    """

    def __init__(self, code_hierarchy: Dict[str, Dict[str, str]]):
        """Инициализация агрегатора.

        Args:
            code_hierarchy: Словарь с информацией о кодах.
                           Формат: {code: {"name": str, "parent": str, "level": int}}
        """
        self.code_hierarchy = code_hierarchy
        self.root_codes = self._find_root_codes()

    def _find_root_codes(self) -> List[str]:
        """Найти корневые коды (разделы)."""
        all_codes = set(self.code_hierarchy.keys())
        child_codes = {info["parent"]
                       for info in self.code_hierarchy.values() if info["parent"]}
        return [code for code in all_codes if code not in child_codes]

    def _get_parent(self, code: str) -> Optional[str]:
        """Получить родительский код."""
        return self.code_hierarchy.get(code, {}).get("parent")

    def _get_name(self, code: str) -> str:
        """Получить название кода."""
        return self.code_hierarchy.get(code, {}).get("name", code)

    def _get_level(self, code: str) -> int:
        """Получить уровень кода."""
        return self.code_hierarchy.get(code, {}).get("level", 0)

    def aggregate(self, lines: List[tuple]) -> Dict[str, AggregatedNode]:
        """Агрегировать строки нагрузки в дерево.

        Args:
            lines: Список строк нагрузки в формате (code, mass, x, y, z)

        Returns:
            Словарь корневых узлов {code: AggregatedNode}
        """
        # Сначала агрегируем на уровне листьев (самых глубоких кодов)
        leaf_nodes: Dict[str, AggregatedNode] = {}

        for code, mass, x, y, z in lines:
            if code not in leaf_nodes:
                leaf_nodes[code] = AggregatedNode(
                    code=code,
                    name=self._get_name(code),
                    level=self._get_level(code)
                )
            leaf_nodes[code].add_line(code, mass, x, y, z)

        # Строим дерево, поднимаясь вверх по иерархии
        result = {}

        for code, node in leaf_nodes.items():
            # Найти корневой путь
            current = code
            path = []
            while current:
                path.append(current)
                current = self._get_parent(current)

            # Вставить узел в дерево
            if not path:
                continue

            root_code = path[-1]
            if root_code not in result:
                result[root_code] = AggregatedNode(
                    code=root_code,
                    name=self._get_name(root_code),
                    level=self._get_level(root_code)
                )

            # Пройти по пути и добавить узлы
            current_node = result[root_code]
            for level_code in reversed(path[:-1]):
                if level_code not in current_node.children:
                    current_node.children[level_code] = AggregatedNode(
                        code=level_code,
                        name=self._get_name(level_code),
                        level=self._get_level(level_code)
                    )
                current_node = current_node.children[level_code]

            # Добавить листовой узел
            if code != root_code:
                if code not in current_node.children:
                    current_node.children[code] = node
                else:
                    # Если узел уже существует (несколько строк с одним кодом)
                    current_node.children[code].mass += node.mass
                    current_node.children[code].mx += node.mx
                    current_node.children[code].my += node.my
                    current_node.children[code].mz += node.mz

            # Обновить родительские узлы
            current = code
            while current:
                parent = self._get_parent(current)
                if parent and parent in result:
                    result[parent].mass += node.mass
                    result[parent].mx += node.mx
                    result[parent].my += node.my
                    result[parent].mz += node.mz
                elif parent:
                    # Создать родительский узел, если его нет
                    if parent not in result:
                        result[parent] = AggregatedNode(
                            code=parent,
                            name=self._get_name(parent),
                            level=self._get_level(parent)
                        )
                    result[parent].mass += node.mass
                    result[parent].mx += node.mx
                    result[parent].my += node.my
                    result[parent].mz += node.mz
                current = parent

        return result

    def flatten(self, tree: Dict[str, AggregatedNode]) -> List[AggregatedNode]:
        """Развернуть дерево в плоский список (для отображения в таблице)."""
        result = []

        def traverse(node: AggregatedNode, depth: int = 0):
            node.depth = depth  # Для отступа в UI
            result.append(node)
            for child in sorted(node.children.values(), key=lambda x: x.code):
                traverse(child, depth + 1)

        for root in sorted(tree.values(), key=lambda x: x.code):
            traverse(root)

        return result
