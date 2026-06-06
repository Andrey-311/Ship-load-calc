import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QStackedWidget, QLabel,
    QMessageBox, QInputDialog, QLineEdit
)
from PySide6.QtCore import Qt

from common.api_client import APIClient
from client1.ecr_edit_widget import ECREditWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api = APIClient()
        self.current_project_id = None
        self.setup_ui()
        self.load_projects()

    def setup_ui(self):
        self.setWindowTitle("Constructor - Ship Load Calculator")
        self.setGeometry(100, 100, 1400, 800)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.projects_list = QListWidget()
        self.projects_list.itemClicked.connect(self.on_project_selected)

        self.ecr_list = QListWidget()
        self.ecr_list.itemClicked.connect(self.on_ecr_selected)

        btn_new_project = QPushButton("New Project")
        btn_new_project.clicked.connect(self.new_project)

        btn_new_ecr = QPushButton("New ECR")
        btn_new_ecr.clicked.connect(self.new_ecr)
        btn_new_ecr.setEnabled(False)

        left_layout.addWidget(QLabel("Projects:"))
        left_layout.addWidget(self.projects_list)
        left_layout.addWidget(btn_new_project)
        left_layout.addWidget(QLabel("ECRs:"))
        left_layout.addWidget(self.ecr_list)
        left_layout.addWidget(btn_new_ecr)

        self.stack = QStackedWidget()
        self.empty_widget = QWidget()
        self.stack.addWidget(self.empty_widget)

        layout.addWidget(left_panel, 1)
        layout.addWidget(self.stack, 3)

    def load_projects(self):
        try:
            projects = self.api.get_projects()
            self.projects_list.clear()
            for p in projects:
                self.projects_list.addItem(f"{p['id']}: {p['name']}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load projects: {e}")

    def load_ecrs(self):
        if not self.current_project_id:
            return
        try:
            ecrs = self.api.get_ecr_list(self.current_project_id)
            self.ecr_list.clear()
            for e in ecrs:
                comment = e['comment'][:30] if e['comment'] else ""
                self.ecr_list.addItem(f"#{e['id']}: {comment} ({e['status']})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load ECRs: {e}")

    def on_project_selected(self, item):
        project_id = int(item.text().split(":")[0])
        self.current_project_id = project_id
        self.load_ecrs()
        for btn in self.findChildren(QPushButton):
            if btn.text() == "New ECR":
                btn.setEnabled(True)

    def on_ecr_selected(self, item):
        ecr_id = int(item.text().split("#")[1].split(":")[0])
        edit_widget = ECREditWidget(self.api, self.current_project_id, ecr_id, self)
        edit_widget.on_ecr_updated.connect(self.load_ecrs)

        for i in range(self.stack.count()):
            w = self.stack.widget(i)
            if hasattr(w, 'ecr_id') and w.ecr_id == ecr_id:
                self.stack.setCurrentIndex(i)
                return

        self.stack.addWidget(edit_widget)
        self.stack.setCurrentWidget(edit_widget)

    def new_project(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project name:", QLineEdit.Normal)
        if ok and name:
            try:
                self.api.create_project({"name": name})
                self.load_projects()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def new_ecr(self):
        if not self.current_project_id:
            return
        comment, ok = QInputDialog.getText(self, "New ECR", "Comment:", QLineEdit.Normal)
        if ok:
            try:
                self.api.create_ecr(self.current_project_id, comment or "")
                self.load_ecrs()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
