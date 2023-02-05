from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class BasePanel(QScrollArea):

    def __init__(self, window):
        super().__init__(window.centralWidget())
        self.setWidgetResizable(True)

        self.setWidget(QWidget(self))
        self.widget().setLayout(QVBoxLayout())

        self.widget().layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.widget().layout().setSpacing(2)

    # noinspection PyPep8Naming
    def addWidget(self, *args):
        self.widget().layout().addWidget(*args)

    # noinspection PyPep8Naming
    def insertWidget(self, *args):
        # noinspection PyUnresolvedReferences
        self.widget().layout().insertWidget(*args)
