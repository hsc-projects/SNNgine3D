from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow
)
from typing import Callable

from snngine3d.engine.widgets import ButtonMenuAction


class BaseWindow(QMainWindow):

    def __init__(self, name: str, parent=None):

        super().__init__(parent)

        self.setWindowTitle(name)
        self.setObjectName(name)
        self.resize(1600, 900)
        self.setCentralWidget(QWidget(self))

    @staticmethod
    def connect_ba(ba: ButtonMenuAction, callable_: Callable):
        ba.action().triggered.connect(callable_)
        ba.button().clicked.connect(callable_)
