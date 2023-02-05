from dataclasses import dataclass
import os
from pathlib import Path
from typing import Callable, Optional, Union

from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QStyle
)


@dataclass
class BaseGUIElement:
    name: Optional[str] = None
    icon_name: Optional[str] = None
    status_tip: Optional[str] = None
    checkable: bool = False
    # parent: Optional[QtWidgets.QMainWindow] = None
    connects: Optional[Union[Callable, list[Callable]]] = None
    disabled: bool = False
    window: Optional[QMainWindow] = None

    def _set_checkable(self, obj: Union[QAction, QPushButton]):
        if self.checkable is True:
            obj.setCheckable(True)

    def _set_disabled(self, obj: Union[QAction, QPushButton]):
        if self.disabled is True:
            obj.setDisabled(True)

    def _set_png_icon(self, obj: Union[QAction, QPushButton]):
        if self.icon_name is not None:
            name = self.icon_name
            if (not name.endswith('.png')) and (not name.endswith('.PNG')):
                name += '.png'
            path = str(Path(__file__).parent) + f'/icons/{name}'
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            obj.setIcon(QIcon(path))

    def _set_status_tip(self, obj: Union[QAction, QPushButton]):
        if self.status_tip is not None:
            obj.setStatusTip(self.status_tip)

    def set_std_icon(self, obj: Union[QAction, QPushButton]):
        pixmapi = getattr(QStyle.StandardPixmap, self.icon_name)
        icon = self.window.style().standardIcon(pixmapi)
        obj.setIcon(icon)

    def _init(self, obj):
        self._set_png_icon(obj)
        self._set_status_tip(obj)
        self._set_checkable(obj)
        self._set_disabled(obj)
