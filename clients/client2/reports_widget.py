import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QMessageBox, QHBoxLayout, QComboBox
)

from common.api_client import APIClient


class ReportsWidget(QWidget):
    """Widget for showing reports."""

    def __init__(self, api: APIClient, project_id: int, parent=None):
        super().__init__(parent)
        self.api = api
        self.project_id = project_id
        self.setup_ui()
        self.load_reports()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Load case selector (will be implemented later)
        self.load_case_combo = QComboBox()
        self.load_case_combo.addItem("100% Default", {"08":100, "14":100, "15":100, "16":100, "17":0, "18":0})
        self.load_case_combo.addItem("10% Supplies", {"08":100, "14":10, "15":100, "16":10, "17":0, "18":0})

        btn_refresh = QPushButton("Refresh Reports")
        btn_refresh.clicked.connect(self.load_reports)

        layout.addWidget(QLabel("Load Case:"))
        layout.addWidget(self.load_case_combo)
        layout.addWidget(btn_refresh)

        # Results labels
        self.lw_label = QLabel("Lightweight: -")
        self.dw_label = QLabel("Deadweight: -")
        self.total_label = QLabel("Total Displacement: -")
        self.xg_label = QLabel("Center X: -")
        self.yg_label = QLabel("Center Y: -")
        self.zg_label = QLabel("Center Z: -")
        self.volume_label = QLabel("Volume: -")

        layout.addWidget(self.lw_label)
        layout.addWidget(self.dw_label)
        layout.addWidget(self.total_label)
        layout.addWidget(self.xg_label)
        layout.addWidget(self.yg_label)
        layout.addWidget(self.zg_label)
        layout.addWidget(self.volume_label)

        layout.addStretch()

    def load_reports(self):
        try:
            percentages = self.load_case_combo.currentData()

            # Get lightweight
            lw = self.api.get_lightweight(self.project_id)
            self.lw_label.setText(f"Lightweight: {lw['total_mass']:.3f} t (X={lw['xg']:.2f}, Y={lw['yg']:.2f}, Z={lw['zg']:.2f})")

            # Get total displacement
            td = self.api.get_total_displacement(self.project_id, percentages, include_volume=True)
            self.dw_label.setText(f"Deadweight: {td['deadweight']:.3f} t")
            self.total_label.setText(f"Total Displacement: {td['total_mass']:.3f} t")
            self.xg_label.setText(f"Center X: {td['xg']:.2f} m")
            self.yg_label.setText(f"Center Y: {td['yg']:.2f} m")
            self.zg_label.setText(f"Center Z: {td['zg']:.2f} m")
            if td.get('volume'):
                self.volume_label.setText(f"Volume: {td['volume']:.3f} m?")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load reports: {e}")
