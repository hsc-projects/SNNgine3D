from PyQt6.QtWidgets import QApplication
import qdarktheme
from vispy import gloo
from vispy.app import Application, Timer


from snngine3d.config_models import EngineConfig


class Engine(Application):

    def __init__(self, config):

        gloo.gl.use_gl('gl+')
        self.config: EngineConfig = config
