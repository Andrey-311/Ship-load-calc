import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView
)

from common.api_client import APIClient


class ActiveLoadWidget(QWidget):
    """Widget for showing active load."""

    def __init__(self, api: APIClient, project_id: int, parent=None):
        super().__init__(parent)
        self.api = api
        self.project_id = project_id
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Code", "Mass (t)", "Xg (m)", "Zg (m)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_data)

        layout.addWidget(self.table)
        layout.addWidget(btn_refresh)

    def load_data(self):
        try:
            data = self.api.get_aggregated_tree(self.project_id)
            
            # ???????? ??? ???? ? ??????? ??????
            items = []
            self.collect_items(data, items)
            
            self.table.setRowCount(len(items))
            for i, item in enumerate(items):
                self.table.setItem(i, 0, QTableWidgetItem(item.get('code', '')))
                self.table.setItem(i, 1, QTableWidgetItem(f"{item.get('mass', 0):.3f}"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{item.get('xg', 0):.2f}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{item.get('zg', 0):.2f}"))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load: {e}")

    def collect_items(self, data, items):
        """?????????? ???????? ??? ???? ?? ??????."""
        if isinstance(data, dict):
            for code, node in data.items():
                if isinstance(node, dict):
                    items.append({
                        'code': code,
                        'mass': node.get('mass', 0),
                        'xg': node.get('xg', 0),
                        'zg': node.get('zg', 0)
                    })
                    # ?????????? ???????????? ?????
                    children = node.get('children', [])
                    if children:
                        self.collect_items(children, items)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    items.append({
                        'code': item.get('code', ''),
                        'mass': item.get('mass', 0),
                        'xg': item.get('xg', 0),
                        'zg': item.get('zg', 0)
                    })
                    children = item.get('children', [])
                    if children:
                        self.collect_items(children, items)
