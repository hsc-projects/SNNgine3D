from typing import Optional

from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QSplitter,
    QStatusBar
)

from vispy.app import Application

from .base_window import BaseWindow
from snngine3d.engine.widgets import AllButtonMenuActions
from .ui_elements import (
    CanvasConfig,
    LocationGroupInfoCanvas,
    LocationGroupInfoPanel,
    MainWindowPanelLeft,
    MainSceneCanvas,
    MenuBar
)
from snngine3d.config_models import PlottingConfig


class MainWindow(BaseWindow):

    def __init__(self,
                 name: str,
                 app: Optional[Application],
                 keys=None
                 ):
        super().__init__(name)

        self.app = app
        self.keys = keys

        for attr in ['ui', 'scene_3d']:
            if hasattr(self, attr):
                raise AttributeError(f'\'{attr}\' ')

        self.all_button_menu_actions = AllButtonMenuActions(self)
        self.menubar = MenuBar(self, self.all_button_menu_actions)

        self.left_panel = MainWindowPanelLeft(self, self.all_button_menu_actions)

        self.menubar.addAction(self.left_panel.synapse_collapsible.add_synapse_visual_button.action())

        self.setMenuBar(self.menubar)
        self.setStatusBar(QStatusBar(self))
        self.scene_3d = MainSceneCanvas(
            conf=CanvasConfig(keys=self.keys), app=self.app,
        )
        self.group_info_scene: Optional[LocationGroupInfoCanvas] = None
        self.right_panel = LocationGroupInfoPanel(self, self.all_button_menu_actions)

        self.splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.scene_3d.frame(parent=self))
        self.splitter.setStretchFactor(0, 16)
        self.splitter.setStretchFactor(1, 3)

        hbox = QHBoxLayout(self.centralWidget())
        hbox.addWidget(self.splitter)

    def add_plotting_config_dependent_widgets(self, plotting_config: PlottingConfig):

        self.scene_3d.add_plot_widgets(plotting_config=plotting_config)

        self.left_panel.add_plotting_config_dependent_widgets(plotting_config=plotting_config)

        if plotting_config.group_info_view_mode.split is True:

            self.group_info_scene = LocationGroupInfoCanvas(
                conf=CanvasConfig(keys=self.keys), app=self.app)
            self.group_info_scene.add_plot_widgets(plotting_config=plotting_config)

            # sync cams between the main scene and the location group scene
            self.scene_3d.network_view.camera.link(self.group_info_scene.view.camera)

            self.splitter.addWidget(self.group_info_scene.frame(self))
            self.splitter.setStretchFactor(2, 2)
            self.splitter.addWidget(self.right_panel)
            self.splitter.setStretchFactor(3, 10)

        if plotting_config.group_info_view_mode.scene is True:
            self.splitter.addWidget(self.right_panel)
            self.splitter.setStretchFactor(2, 10)

