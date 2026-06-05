import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
    QHeaderView, QTextEdit, QDialog, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt

from common.api_client import APIClient


class ECRReviewWidget(QWidget):
    """Widget for reviewing ECRs."""

    def __init__(self, api: APIClient, project_id: int, parent=None):
        super().__init__(parent)
        self.api = api
        self.project_id = project_id
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Table for ECRs
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Status", "Comment", "Total Mass", "Created"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemDoubleClicked.connect(self.on_ecr_double_click)

        # Refresh button
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_data)

        layout.addWidget(QLabel("ECRs awaiting review:"))
        layout.addWidget(self.table)
        layout.addWidget(btn_refresh)

    def load_data(self):
        try:
            ecrs = self.api.get_ecr_list(self.project_id, status="review")
            self.table.setRowCount(len(ecrs))

            for i, ecr in enumerate(ecrs):
                self.table.setItem(i, 0, QTableWidgetItem(str(ecr['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(ecr['status']))
                self.table.setItem(i, 2, QTableWidgetItem(ecr.get('comment', '')[:50]))
                self.table.setItem(i, 3, QTableWidgetItem(f"{ecr.get('total_mass', 0):.3f}"))
                self.table.setItem(i, 4, QTableWidgetItem(ecr['created_at'][:19]))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load ECRs: {e}")

    def on_ecr_double_click(self, item):
        row = item.row()
        ecr_id = int(self.table.item(row, 0).text())
        self.show_ecr_details(ecr_id)

    def show_ecr_details(self, ecr_id: int):
        """Show ECR details and approve/reject dialog."""
        try:
            lines = self.api.get_ecr_lines(self.project_id, ecr_id)
            cg = self.api.get_center_of_gravity(self.project_id, ecr_id)

            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"ECR #{ecr_id} Details")
            dialog.setMinimumSize(800, 500)

            layout = QVBoxLayout(dialog)

            # Info
            info = QLabel(f"Total Mass: {cg['total_mass']:.3f} t\n"
                         f"Center of Gravity: X={cg['xg']:.2f}, Y={cg['yg']:.2f}, Z={cg['zg']:.2f}")
            layout.addWidget(info)

            # Lines table
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Code", "Mass", "X", "Y", "Z"])
            table.setRowCount(len(lines))
            for i, line in enumerate(lines):
                table.setItem(i, 0, QTableWidgetItem(line['code']))
                table.setItem(i, 1, QTableWidgetItem(f"{line['mass']:.3f}"))
                table.setItem(i, 2, QTableWidgetItem(f"{line['x']:.2f}"))
                table.setItem(i, 3, QTableWidgetItem(f"{line['y']:.2f}"))
                table.setItem(i, 4, QTableWidgetItem(f"{line['z']:.2f}"))
            layout.addWidget(table)

            # Buttons
            btn_layout = QHBoxLayout()
            btn_approve = QPushButton("Approve")
            btn_reject = QPushButton("Reject")
            btn_cancel = QPushButton("Cancel")

            btn_approve.clicked.connect(lambda: self.approve_ecr(ecr_id, dialog))
            btn_reject.clicked.connect(lambda: self.reject_ecr(ecr_id, dialog))
            btn_cancel.clicked.connect(dialog.reject)

            btn_layout.addWidget(btn_approve)
            btn_layout.addWidget(btn_reject)
            btn_layout.addWidget(btn_cancel)
            layout.addLayout(btn_layout)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load ECR details: {e}")

    def approve_ecr(self, ecr_id: int, dialog: QDialog):
        try:
            self.api.update_ecr_status(self.project_id, ecr_id, "approved")
            QMessageBox.information(self, "Success", "ECR approved successfully")
            dialog.accept()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to approve: {e}")

    def reject_ecr(self, ecr_id: int, dialog: QDialog):
        # Show rejection reason input
        reason_dialog = QDialog(self)
        reason_dialog.setWindowTitle("Rejection Reason")
        layout = QFormLayout(reason_dialog)

        reason_text = QTextEdit()
        reason_text.setPlaceholderText("Enter reason for rejection...")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout.addRow("Reason:", reason_text)
        layout.addRow(buttons)

        buttons.accepted.connect(reason_dialog.accept)
        buttons.rejected.connect(reason_dialog.reject)

        if reason_dialog.exec():
            try:
                self.api.update_ecr_status(
                    self.project_id, ecr_id, "rejected",
                    rejection_reason=reason_text.toPlainText()
                )
                QMessageBox.information(self, "Success", "ECR rejected")
                dialog.accept()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reject: {e}")
