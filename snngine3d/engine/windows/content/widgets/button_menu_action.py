from dataclasses import dataclass
from typing import Optional, Union

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QPushButton
)
from .base_gui_element import BaseGUIElement


class PushButton(QPushButton):

    def __init__(self, name, *args):
        QPushButton.__init__(self, name, *args)
        self.setFixedHeight(28)
        if name is None:
            self.setFixedWidth(28)


@dataclass
class ButtonMenuAction(BaseGUIElement):
    """ Equivalent pushbutton and menu-action."""
    menu_name: Optional[str] = None
    menu_short_cut: Optional[str] = None
    _action = None
    _button = None

    def __post_init__(self):
        if (self.connects is not None) and (not isinstance(self.connects, list)):
            self.connects = [self.connects]
        if (self.menu_short_cut is not None) and (self.status_tip is not None):
            self.status_tip = self.status_tip + f" ({self.menu_short_cut})"
            print(self.status_tip)

    def _set_menu_short_cut(self, obj: Union[QAction, QPushButton]):
        if self.menu_short_cut is not None:
            obj.setShortcut(self.menu_short_cut)

    def action(self):
        if self._action is None:
            self._action = QAction(self.menu_name, self.window)
            self._set_menu_short_cut(self._action)
            self._init(self._action)
            if self.connects is not None:
                for callable_ in self.connects:
                    self._action.triggered.connect(callable_)
        return self._action

    def button(self):
        if self._button is None:
            self._button: QPushButton = PushButton(self.name, self.window)
            self._init(self._button)
            if self.connects is not None:
                for callable_ in self.connects:
                    self._button.clicked.connect(callable_)
            self._button.clicked.connect(self.button_clicked)
        return self._button

    def button_clicked(self):
        sender = self.window.sender()
        # noinspection PyUnresolvedReferences
        msg = f'Clicked: {sender.text()}'
        self.window.statusBar().showMessage(msg)
