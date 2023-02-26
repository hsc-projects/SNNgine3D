import numba
from PyQt6.QtWidgets import QApplication
import qdarktheme
from typing import Callable, Optional
from vispy import gloo
from vispy.app import Application, Timer

from .windows import MainWindow

from snngine3d.config_models import EngineConfig
# from snngine3d.engine.widgets import ButtonMenuAction
from snngine3d.nn import VisualizedSpatialNeuralNetwork


class Engine(Application):

    class UI:

        def __init__(self, main_window: MainWindow):
            self.START_SIMULATION = main_window.all_button_menu_actions.START_SIMULATION
            self.PAUSE_SIMULATION = main_window.all_button_menu_actions.PAUSE_SIMULATION
            self.EXIT_APP = main_window.all_button_menu_actions.EXIT_APP

            self.ADD_SELECTOR_BOX = main_window.all_button_menu_actions.ADD_SELECTOR_BOX
            self.TOGGLE_OUTERGRID = main_window.all_button_menu_actions.TOGGLE_OUTERGRID

            self.ADD_SYNAPSE_VISUAL = main_window.left_panel.synapse_collapsible.ADD_SYNAPSE_VISUAL

    def __init__(self, config: Optional[EngineConfig] = None):

        from pycuda import autoinit
        gloo.gl.use_gl('gl+')

        super().__init__(backend_name='pyqt6')

        self.native_app = QApplication([''])
        self.native_app.setStyleSheet(qdarktheme.load_stylesheet())

        self.main_window: MainWindow = MainWindow(name="SNN Engine", app=self)

        self.ui = self.UI(self.main_window)

        self.main_window.show()

        self._connect_ui()

        self.config: Optional[EngineConfig] = None

        self.simulation_timer = Timer('auto', connect=self.update, start=False)

        self.network = None
        if config is not None:
            self.load_config(config)

        self.main_window.scene_3d.set_current()

        self._add_selector_box()

    def _add_selector_box(self):
        # self.main_window.scene_3d.set_current()
        s = self.network.add_selector_box(
            self.main_window.scene_3d, self.main_window.scene_3d.network_view)
        self.main_window.left_panel.rendered_objects_collapsible.add_object(s)

    def _add_synapsevisual(self):
        self.main_ui_panel.synapse_collapsible.add_interfaced_synapse(self.network, 0)

    def _connect_ui(self):

        self.main_window.connect_ba(self.ui.START_SIMULATION, self._trigger_update_switch)
        self.main_window.connect_ba(self.ui.PAUSE_SIMULATION, self._trigger_update_switch)
        self.main_window.connect_ba(self.ui.EXIT_APP, self.quit)
        self.main_window.connect_ba(self.ui.TOGGLE_OUTERGRID, self._toggle_outergrid)
        self.main_window.connect_ba(self.ui.ADD_SELECTOR_BOX, self._add_selector_box)
        self.main_window.connect_ba(self.ui.ADD_SYNAPSE_VISUAL, self._add_synapsevisual)

    def _toggle_outergrid(self):
        self.network.outer_grid.visible = not self.network.outer_grid.visible

        if self.network.outer_grid.visible is True:
            self.main_ui_panel.buttons.toggle_outergrid.setChecked(True)
            self.actions.toggle_outergrid.setChecked(True)

            if self._group_info_view_mode.scene is True:
                self.main_window.scene_3d.group_firings_multiplot.visible = True
            if self.neuron_plot_window is not None:
                self.neuron_plot_window.hide()

        else:
            self.main_ui_panel.buttons.toggle_outergrid.setChecked(False)
            self.actions.toggle_outergrid.setChecked(False)
            if self._group_info_view_mode.scene is True:
                self.main_window.scene_3d.group_firings_multiplot.visible = False
            if self.neuron_plot_window is not None:
                self.neuron_plot_window.show()

    def _trigger_update_switch(self):
        if self.simulation_timer.running is True:
            self.simulation_timer.start()
            self.ui.START_SIMULATION.button().setDisabled(True)
            self.ui.START_SIMULATION.action().setDisabled(True)
            self.ui.PAUSE_SIMULATION.button().setDisabled(False)
            self.ui.PAUSE_SIMULATION.action().setDisabled(False)
        else:
            self.time_elapsed_until_last_off += self.simulation_timer.elapsed
            self.simulation_timer.stop()
            self.ui.START_SIMULATION.button().setDisabled(False)
            self.ui.START_SIMULATION.action().setDisabled(False)
            self.ui.PAUSE_SIMULATION.button().setDisabled(True)
            self.ui.PAUSE_SIMULATION.action().setDisabled(True)

    def _set_screen(self):
        if self.config is not None:
            screen = self.config.screen
        else:
            screen = 0
        self.main_window.setGeometry(self.native_app.screens()[screen].availableGeometry())

    def load_config(self, config: EngineConfig):
        print(config.network, '\n')
        print(config.network.chemical_configs, '\n')
        print(config.plotting, '\n')
        self.config = config
        self.main_window.add_plotting_config_dependent_widgets(plotting_config=config.plotting)
        self._set_screen()

        self.network = VisualizedSpatialNeuralNetwork(self)

        self.main_window.scene_3d.network = self.network
        # noinspection PyUnresolvedReferences
        self.native_app.aboutToQuit.connect(self.network.unregister_registered_buffers)

    # noinspection PyUnusedLocal
    def update(self, event):
        if self.update_switch is True:
            self.network.simulation_gpu.update()
            t = self.network.simulation_gpu.Simulation.t
            t_str = str(t)
            if self.neuron_plot_window:
                self.neuron_plot_window.voltage_plot_sc.update()
                self.neuron_plot_window.scatter_plot_sc.update()
                # self.neuron_plot_window.voltage_plot_sc.table.t.text = t
                # self.neuron_plot_window.scatter_plot_sc.table.t.text = t
            if self._group_info_view_mode.split is True:
                self.main_window.group_info_scene.update()
                # self.main_window.group_info_scene.table.t.text = t
            self.main_window.scene_3d.table.t.text = t_str
            self.main_window.scene_3d.table.update_duration.text = str(
                self.network.simulation_gpu.Simulation.update_duration)

            if self.config.update_single_neuron_plots is True:
                self.interfaced_neuron_collection.update_interfaced_neuron_plots(t)

