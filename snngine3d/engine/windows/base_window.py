from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow
)


class BaseWindow(QMainWindow):

    def __init__(self, name: str, parent=None):

        super().__init__(parent)

        self.setWindowTitle(name)
        self.setObjectName(name)
        self.resize(1600, 900)
        self.setCentralWidget(QWidget(self))
