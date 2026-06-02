"""Client 1: Designer - entry point."""

import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ship Load Designer")
        self.setCentralWidget(QLabel("Client 1 - Конструктор\n(в разработке)"))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
