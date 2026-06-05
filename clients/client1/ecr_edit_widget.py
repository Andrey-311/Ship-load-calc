import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGroupBox, QFormLayout, QLineEdit, QMessageBox,
    QDialog, QDialogButtonBox, QDoubleSpinBox
)
from PySide6.QtCore import Signal

from common.widgets.table_widget import LoadLineTableView
from common.api_client import APIClient


class ECREditWidget(QWidget):
    on_ecr_updated = Signal()

    def __init__(self, api: APIClient, project_id: int, ecr_id: int, parent=None):
        super().__init__(parent)
        self.api = api
        self.project_id = project_id
        self.ecr_id = ecr_id
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        info_group = QGroupBox("ECR Information")
        info_layout = QFormLayout(info_group)
        self.lbl_ecr_id = QLabel(str(self.ecr_id))
        self.lbl_status = QLabel("Loading...")
        info_layout.addRow("ECR ID:", self.lbl_ecr_id)
        info_layout.addRow("Status:", self.lbl_status)
        layout.addWidget(info_group)

        self.table = LoadLineTableView()
        layout.addWidget(QLabel("Load Lines:"))
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_submit = QPushButton("Submit for Review")
        self.btn_submit.clicked.connect(self.submit_ecr)
        self.btn_submit.setEnabled(False)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.load_data)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_submit)
        layout.addLayout(btn_layout)

        self.cg_label = QLabel("Center of Gravity: Loading...")
        layout.addWidget(self.cg_label)

        self.table.btn_add.clicked.connect(self.add_line)
        self.table.btn_edit.clicked.connect(self.edit_line)
        self.table.btn_delete.clicked.connect(self.delete_line)

    def load_data(self):
        try:
            lines = self.api.get_ecr_lines(self.project_id, self.ecr_id)
            self.table.setLines(lines)

            ecr = self.api.get_ecr(self.project_id, self.ecr_id)
            self.lbl_status.setText(ecr.get('status', 'unknown'))
            self.btn_submit.setEnabled(ecr.get('status') == 'draft')

            cg = self.api.get_center_of_gravity(self.project_id, self.ecr_id)
            self.cg_label.setText(
                f"Center of Gravity: X={cg.get('xg', 0):.2f} m, "
                f"Y={cg.get('yg', 0):.2f} m, Z={cg.get('zg', 0):.2f} m, "
                f"Mass={cg.get('total_mass', 0):.3f} t"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {e}")

    def add_line(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Load Line")
        layout = QFormLayout(dialog)

        code_edit = QLineEdit()
        mass_spin = QDoubleSpinBox()
        mass_spin.setRange(-1000000, 1000000)
        mass_spin.setDecimals(3)
        mass_spin.setValue(0)
        x_spin = QDoubleSpinBox()
        x_spin.setRange(-1000, 1000)
        x_spin.setDecimals(2)
        y_spin = QDoubleSpinBox()
        y_spin.setRange(-1000, 1000)
        y_spin.setDecimals(2)
        z_spin = QDoubleSpinBox()
        z_spin.setRange(0, 1000)
        z_spin.setDecimals(2)

        layout.addRow("Code:", code_edit)
        layout.addRow("Mass (t):", mass_spin)
        layout.addRow("X (m):", x_spin)
        layout.addRow("Y (m):", y_spin)
        layout.addRow("Z (m):", z_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec():
            try:
                self.api.create_load_line(self.project_id, self.ecr_id, {
                    "code": code_edit.text(),
                    "mass": mass_spin.value(),
                    "x": x_spin.value(),
                    "y": y_spin.value(),
                    "z": z_spin.value()
                })
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def edit_line(self):
        row = self.table.getSelectedRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", "Select a line to edit")
            return

        line = self.table.getLine(row)
        if not line:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Load Line")
        layout = QFormLayout(dialog)

        code_edit = QLineEdit(str(line.get('code', '')))
        mass_spin = QDoubleSpinBox()
        mass_spin.setRange(-1000000, 1000000)
        mass_spin.setDecimals(3)
        mass_spin.setValue(line.get('mass', 0))
        x_spin = QDoubleSpinBox()
        x_spin.setRange(-1000, 1000)
        x_spin.setDecimals(2)
        x_spin.setValue(line.get('x', 0))
        y_spin = QDoubleSpinBox()
        y_spin.setRange(-1000, 1000)
        y_spin.setDecimals(2)
        y_spin.setValue(line.get('y', 0))
        z_spin = QDoubleSpinBox()
        z_spin.setRange(0, 1000)
        z_spin.setDecimals(2)
        z_spin.setValue(line.get('z', 0))

        layout.addRow("Code:", code_edit)
        layout.addRow("Mass (t):", mass_spin)
        layout.addRow("X (m):", x_spin)
        layout.addRow("Y (m):", y_spin)
        layout.addRow("Z (m):", z_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec():
            try:
                self.api.update_load_line(self.project_id, self.ecr_id, line['id'], {
                    "code": code_edit.text(),
                    "mass": mass_spin.value(),
                    "x": x_spin.value(),
                    "y": y_spin.value(),
                    "z": z_spin.value()
                })
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_line(self):
        row = self.table.getSelectedRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", "Select a line to delete")
            return

        reply = QMessageBox.question(self, "Confirm", "Delete this line?",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            line = self.table.getLine(row)
            if line:
                try:
                    self.api.delete_load_line(self.project_id, self.ecr_id, line['id'])
                    self.load_data()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

    def submit_ecr(self):
        reply = QMessageBox.question(self, "Confirm", 
                                      "Submit ECR for review?",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.api.update_ecr_status(self.project_id, self.ecr_id, "review")
                self.load_data()
                self.on_ecr_updated.emit()
                QMessageBox.information(self, "Success", "ECR submitted for review")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
