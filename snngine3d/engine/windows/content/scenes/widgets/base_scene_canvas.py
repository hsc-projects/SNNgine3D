from dataclasses import asdict
from PyQt6.QtWidgets import QFrame, QVBoxLayout
from vispy.scene import SceneCanvas

from snngine3d.engine.windows.content.scenes.canvas_config import CanvasConfig


class SceneCanvasFrame(QFrame):

    def __init__(self, parent, canvas: SceneCanvas):
        super().__init__(parent)
        self.canvas = canvas
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(canvas.native)


class BaseEngineSceneCanvas(SceneCanvas):

    # noinspection PyTypeChecker
    def __init__(self,
                 conf: CanvasConfig,
                 app):  # Optional[Application]):

        conf = conf or CanvasConfig()
        super().__init__(**asdict(conf), app=app)

        self.central_widget.margin = 5

    def frame(self, parent):
        return SceneCanvasFrame(parent=parent, canvas=self)
