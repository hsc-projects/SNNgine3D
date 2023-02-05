from dataclasses import dataclass
from typing import Optional, Union

from vispy.app import Canvas
from vispy.color import Color
from vispy.gloo import GLContext


@dataclass
class CanvasConfig:
    title: str = 'VisPy canvas'
    size: tuple = (1600, 1200)
    position: Optional[tuple] = None
    show: bool = False
    autoswap: bool = True

    create_native: bool = True
    vsync: bool = False
    resizable: bool = True
    decorate: bool = True
    fullscreen: bool = False
    config: Optional[dict] = None
    shared = Optional[Union[Canvas, GLContext]]
    keys: Optional[Union[str, dict]] = 'interactive'
    parent: Optional = None
    dpi: Optional[float] = None
    always_on_top: bool = False
    px_scale: int = 1
    bgcolor: Union[str, Color] = 'black'
