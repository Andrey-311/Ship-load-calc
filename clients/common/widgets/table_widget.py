from PySide6.QtWidgets import (
    QTableView, QWidget, QVBoxLayout, QPushButton,
    QHBoxLayout, QHeaderView
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from typing import List, Dict, Optional


class LoadLineTableModel(QAbstractTableModel):
    HEADERS = ["Code", "Mass (t)", "X (m)", "Y (m)", "Z (m)", "Mx (tm)", "My (tm)", "Mz (tm)", "ID"]

    def __init__(self, lines: List[Dict] = None):
        super().__init__()
        self._lines = lines or []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._lines)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Optional[str]:
        if not index.isValid():
            return None
        line = self._lines[index.row()]
        col = index.column()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if col == 0:
                return line.get("code", "")
            elif col == 1:
                return f"{line.get('mass', 0):.3f}"
            elif col == 2:
                return f"{line.get('x', 0):.2f}"
            elif col == 3:
                return f"{line.get('y', 0):.2f}"
            elif col == 4:
                return f"{line.get('z', 0):.2f}"
            elif col == 5:
                return f"{line.get('mass', 0) * line.get('x', 0):.1f}"
            elif col == 6:
                return f"{line.get('mass', 0) * line.get('y', 0):.1f}"
            elif col == 7:
                return f"{line.get('mass', 0) * line.get('z', 0):.1f}"
            elif col == 8:
                return str(line.get("id", ""))
        if role == Qt.TextAlignmentRole and col >= 1:
            return Qt.AlignRight | Qt.AlignVCenter
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Optional[str]:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]
        return None

    def setLines(self, lines: List[Dict]):
        self.beginResetModel()
        self._lines = lines
        self.endResetModel()

    def addLine(self, line: Dict):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._lines.append(line)
        self.endInsertRows()

    def updateLine(self, row: int, line: Dict):
        if 0 <= row < len(self._lines):
            self._lines[row] = line
            self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))

    def deleteLine(self, row: int):
        if 0 <= row < len(self._lines):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._lines.pop(row)
            self.endRemoveRows()

    def getLine(self, row: int) -> Optional[Dict]:
        if 0 <= row < len(self._lines):
            return self._lines[row]
        return None

    def clear(self):
        self.beginResetModel()
        self._lines = []
        self.endResetModel()


class LoadLineTableView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.model = LoadLineTableModel()
        self.table.setModel(self.model)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Delete")
        self.btn_clear = QPushButton("Clear")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)

    def setLines(self, lines: List[Dict]):
        self.model.setLines(lines)

    def getSelectedRow(self) -> int:
        selection = self.table.selectionModel().selectedRows()
        if selection:
            return selection[0].row()
        return -1

    def getLine(self, row: int) -> Optional[Dict]:
        return self.model.getLine(row)

    def clear(self):
        self.model.clear()
