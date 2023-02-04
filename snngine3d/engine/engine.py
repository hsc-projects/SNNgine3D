from PyQt6.QtWidgets import QApplication
import qdarktheme
import sys
import typer
from typing import Optional
from vispy import gloo
from vispy.app import Application, Timer

from snngine3d.config_models import EngineConfig
from .windows import MainWindow


class Engine(Application):

    def __init__(self, config: Optional[EngineConfig] = None):

        gloo.gl.use_gl('gl+')
        self.native_app = QApplication([''])
        super().__init__(backend_name='pyqt6')

        self.config: Optional[EngineConfig] = None

        self.native_app.setStyleSheet(qdarktheme.load_stylesheet())

        self.main_window: MainWindow = MainWindow(
            name="SNN Engine", app=self,
            # plotting_config=self._plotting_config
        )
        self.main_window.show()
        if config is not None:
            self.load_config(config)

    def load_config(self, config: EngineConfig):
        print(config.network, '\n')
        print(config.network.chemical_configs, '\n')
        print(config.plotting, '\n')
        self.config = config
        self.main_window.add_plot_widgets(plotting_config=config.plotting)
