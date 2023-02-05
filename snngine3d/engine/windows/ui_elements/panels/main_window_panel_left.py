from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QWidget,
)

from snngine3d.engine.widgets.collapsibles import (
    ChemicalControlCollapsibleContainer,
    MainWindowNeuronsCollapsible,
    RenderedObjectCollectionCollapsible,
    SensoryInputCollapsible,
    SynapticWeightsCollapsible,
    SynapseCollapsibleContainer,
    ThalamicInputCollapsible
)
# from network import SpikingNeuralNetwork
# from network.network_state import MultiModelNeuronStateTensor
from snngine3d.config_models import PlottingConfig
from snngine3d.engine.widgets import AllButtonMenuActions
from .base_panel import BasePanel


class MainWindowPanelLeft(BasePanel):

    class Buttons:
        def __init__(self, buttons: AllButtonMenuActions, parent):
            max_width = 140
            self.start: QPushButton = buttons.START_SIMULATION.button()
            self.pause: QPushButton = buttons.PAUSE_SIMULATION.button()
            self.exit: QPushButton = buttons.EXIT_APP.button()
            # self.add_synapsevisual: QPushButton = buttons.ADD_SYNAPSEVISUAL.button()
            self.add_selector_box: QPushButton = buttons.ADD_SELECTOR_BOX.button()
            self.toggle_outergrid: QPushButton = buttons.TOGGLE_OUTERGRID.button()

            self.toggle_outergrid.setMinimumWidth(max_width)
            self.toggle_outergrid.setMaximumWidth(max_width)
            self.start.setMaximumWidth(max_width)
            self.exit.setMaximumWidth(max_width)

            self.play_pause_widget = QWidget(parent)
            self.play_pause_widget.setFixedSize(95, 45)
            play_pause_hbox = QHBoxLayout(self.play_pause_widget)
            play_pause_hbox.setContentsMargins(0, 0, 0, 0)
            play_pause_hbox.setSpacing(2)
            play_pause_hbox.addWidget(self.start)
            play_pause_hbox.addWidget(self.pause)

    def __init__(self, window: QMainWindow, buttons: AllButtonMenuActions):

        BasePanel.__init__(self, window)

        self.window: QMainWindow = window

        self.buttons = self.Buttons(buttons=buttons, parent=self)

        self.neurons_collapsible = None
        self.chemicals_collapsible = ChemicalControlCollapsibleContainer(parent=self)
        self.synapse_collapsible = SynapseCollapsibleContainer(parent=self, window=window)
        self.sensory_input_collapsible = SensoryInputCollapsible(parent=self, window=window)
        self.thalamic_input_collapsible = ThalamicInputCollapsible(parent=self, window=window)

        self.weights_collapsible = SynapticWeightsCollapsible(self, window=window)

        self.rendered_objects_collapsible = RenderedObjectCollectionCollapsible(self)

        self.addWidget(self.buttons.play_pause_widget)
        self.addWidget(self.buttons.toggle_outergrid)
        self.addWidget(self.chemicals_collapsible)

        self.addWidget(self.synapse_collapsible)
        self.addWidget(self.weights_collapsible)
        self.addWidget(self.sensory_input_collapsible)
        self.addWidget(self.thalamic_input_collapsible)

        self.addWidget(self.buttons.add_selector_box)
        self.addWidget(self.rendered_objects_collapsible)

        self.addWidget(self.buttons.exit)

    def add_plotting_config_dependent_widgets(self, plotting_config: PlottingConfig):
        if plotting_config.windowed_neuron_interfaces is False:
            self.neurons_collapsible = MainWindowNeuronsCollapsible(parent=self)
        if plotting_config.windowed_neuron_interfaces is False:
            self.insertWidget(2, self.neurons_collapsible)

