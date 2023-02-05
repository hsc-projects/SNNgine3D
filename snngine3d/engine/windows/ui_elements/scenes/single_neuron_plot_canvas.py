from typing import Optional

from vispy.app import Application

from snngine3d.config_models import PlottingConfig
from .widgets import (
    BaseEngineSceneCanvas,
    SingleNeuronPlotWidget,
)
from .canvas_config import CanvasConfig


class SingleNeuronPlotCanvas(BaseEngineSceneCanvas):
    def __init__(self,
                 conf: CanvasConfig,
                 app: Optional[Application],
                 width_min=300, width_max=300, height_min=190, height_max=190):

        super().__init__(conf, app)

        self.unfreeze()

        self._width_min = width_min
        self._width_max = width_max
        self._height_min = height_min
        self._height_max = height_max

        self.plot_widget = None
        self.grid = self.central_widget.add_grid()
        self.freeze()

    def add_plot_widget(self, plotting_config: PlottingConfig):
        self.plot_widget = SingleNeuronPlotWidget(plotting_confing=plotting_config,
                                                  width_min=self._width_min,
                                                  width_max=self._width_max,
                                                  height_min=self._height_min,
                                                  height_max=self._height_max)
        self.grid.add_widget(self.plot_widget)
