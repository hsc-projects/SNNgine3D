from typing import Optional

from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QSplitter,
    QWidget,
    QMainWindow,
    QStatusBar
)

from vispy.app import Application
#
# from engine.content.scenes import (
#     MainSceneCanvas,
#     LocationGroupInfoCanvas,
#     ScatterPlotSceneCanvas,
#     VoltagePlotSceneCanvas
# )
#
from .base_window import BaseWindow
from .content import (
    AllButtonMenuActions,
    CanvasConfig,
    # MainUILeft,
    MainSceneCanvas,
    MenuBar,
    # ButtonMenuActions,
    # GroupInfoPanel,
    # SceneCanvasFrame,
    # NeuronInterfacePanel
)
from snngine3d.config_models import PlottingConfig


class MainWindow(BaseWindow):

    def __init__(self,
                 name: str,
                 app: Optional[Application],
                 # plotting_config: PlottingConfig,
                 keys=None
                 ):
        super().__init__(name)

        self.app = app

        for attr in ['ui', 'scene_3d']:
            if hasattr(self, attr):
                raise AttributeError(f'\'{attr}\' ')

        self.ui_elements = AllButtonMenuActions(self)
        self.menubar = MenuBar(self, self.ui_elements)

        # self.ui_panel_left = MainUILeft(self, plotting_config)

        self.setMenuBar(self.menubar)
        self.setStatusBar(QStatusBar(self))
        self.scene_3d = MainSceneCanvas(
            conf=CanvasConfig(keys=keys), app=app,
            # plotting_config=plotting_config
        )
        # if plotting_config.group_info_view_mode.split is True:
        #     self.group_info_scene = LocationGroupInfoCanvas(
        #         conf=CanvasConfig(keys=keys), app=app, plotting_config=plotting_config)
        #     self.scene_3d.network_view.camera.link(
        #         self.group_info_scene.view.camera)
        #     self.ui_right = GroupInfoPanel(self)

        self.splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        # self.splitter.addWidget(self.ui_panel_left)
        self.splitter.addWidget(self.scene_3d.frame(parent=self))
        self.splitter.setStretchFactor(0, 16)
        self.splitter.setStretchFactor(1, 3)

        # if plotting_config.group_info_view_mode.scene is True:
        #     self.ui_right = GroupInfoPanel(self)
        #     self.splitter.addWidget(self.ui_right)
        #     # self.splitter.setStretchFactor(1, 6)
        #     self.splitter.setStretchFactor(2, 10)

        hbox = QHBoxLayout(self.centralWidget())
        hbox.addWidget(self.splitter)

    def add_plot_widgets(self, plotting_config: PlottingConfig):
        self.scene_3d.add_plot_widgets(plotting_config=plotting_config)

    # def add_group_info_scene_to_splitter(self, plotting_config):
    #     if plotting_config.group_info_view_mode.split is True:
    #         self.splitter.addWidget(SceneCanvasFrame(self, self.group_info_scene))
    #         self.splitter.setStretchFactor(2, 2)
    #         self.splitter.addWidget(self.ui_right)
    #         self.splitter.setStretchFactor(3, 10)
