from typing import Optional

from vispy.app import Application
from vispy.visuals.transforms import STTransform
from vispy.scene import XYZAxis, Widget

from snngine3d.config_models import PlottingConfig
from .widgets import (
    BaseEngineSceneCanvas,
    GroupFiringsPlotWidget,
    GroupInfoColorBar,
    TextTableWidget,
)
from .canvas_config import CanvasConfig


class LocationGroupInfoCanvas(BaseEngineSceneCanvas):

    def __init__(self, conf: CanvasConfig, app: Optional[Application],
                 display_time: bool = False):

        super().__init__(conf, app)
        self.unfreeze()
        self.view = self.central_widget.add_view()
        self.view.camera = 'turntable'
        axis = XYZAxis(parent=self.view.scene)
        axis.transform = STTransform()
        axis.transform.move((-0.1, -0.1, -0.1))

        self.grid = self.view.add_grid()

        if display_time is True:
            self.table = TextTableWidget(labels=['t'], height_max_global=25)
            self.table.height_max = 25
            self.grid.add_widget(self.table, 0, 6)

        self.group_firings_multiplot = None
        self.group_firings_multiplot_placeholder = Widget()

        self.color_bar = GroupInfoColorBar()
        self.freeze()

    def add_plot_widgets(self, plotting_config: PlottingConfig):
        self.grid.add_widget(self.color_bar, 5, 0, 6, 1)
        if plotting_config.has_group_firings_multiplot:

            self.group_firings_multiplot = GroupFiringsPlotWidget(plotting_confing=plotting_config, width_max=600)
            self.grid.add_widget(self.group_firings_multiplot, 5, 5, col_span=2, row_span=6)
        else:
            self.grid.add_widget(self.group_firings_multiplot_placeholder, 5, 5, col_span=2, row_span=6)
