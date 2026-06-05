import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QStackedWidget, QLabel,
    QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt

from common.api_client import APIClient
from client2.ecr_review_widget import ECRReviewWidget
from client2.active_load_widget import ActiveLoadWidget
from client2.reports_widget import ReportsWidget


class MainWindow(QMainWindow):
    """Main window for Calculator."""

    def __init__(self):
        super().__init__()
        self.api = APIClient()
        self.current_project_id = None
        self.setup_ui()
        self.load_projects()

    def setup_ui(self):
        self.setWindowTitle("Calculator - Ship Load Calculator")
        self.setGeometry(100, 100, 1400, 800)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Left panel - projects list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.projects_list = QListWidget()
        self.projects_list.itemClicked.connect(self.on_project_selected)

        left_layout.addWidget(QLabel("Projects:"))
        left_layout.addWidget(self.projects_list)

        # Right panel - tabs for different views
        self.tabs = QTabWidget()
        self.ecr_review_widget = QWidget()
        self.active_load_widget = QWidget()
        self.reports_widget = QWidget()

        self.tabs.addTab(self.ecr_review_widget, "ECR Review")
        self.tabs.addTab(self.active_load_widget, "Active Load")
        self.tabs.addTab(self.reports_widget, "Reports")

        layout.addWidget(left_panel, 1)
        layout.addWidget(self.tabs, 3)

    def load_projects(self):
        try:
            projects = self.api.get_projects()
            self.projects_list.clear()
            for p in projects:
                self.projects_list.addItem(f"{p['id']}: {p['name']}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load projects: {e}")

    def on_project_selected(self, item):
        project_id = int(item.text().split(":")[0])
        self.current_project_id = project_id

        # Update all tabs with new project
        self.ecr_review_widget = ECRReviewWidget(self.api, project_id, self)
        self.active_load_widget = ActiveLoadWidget(self.api, project_id, self)
        self.reports_widget = ReportsWidget(self.api, project_id, self)

        self.tabs.clear()
        self.tabs.addTab(self.ecr_review_widget, "ECR Review")
        self.tabs.addTab(self.active_load_widget, "Active Load")
        self.tabs.addTab(self.reports_widget, "Reports")
