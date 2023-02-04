from dataclasses import dataclass, asdict
from typing import Optional

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from snngine3d.engine.windows.content.ui_widgets import SpinBoxSlider
# from engine.content.widgets.combobox_frame import ComboBoxFrame, G2GInfoDualComboBoxFrame
# from engine.content.widgets.gui_element import (
#     ButtonMenuAction
# )
# from engine.content.widgets.rendered_object_collapsible import RenderedObjectCollapsible
# from engine.content.widgets.collapsible_widget.collapsible_widget import CollapsibleWidget
# from network import SpikingNeuralNetwork, PlottingConfig
# from network.network_state import MultiModelNeuronStateTensor
# from .neuron_properties_collapsible import SingleNeuronCollapsible, SingleNeuronCollapsibleContainer
# from .synapse_collapsible import SynapseCollapsibleContainer
# from .chemical_control_collapsible import ChemicalControlCollapsibleContainer
# from utils import boxed_string
# from .widgets.spin_box_sliders import SpinBoxSlider

from snngine3d.engine.windows.content.all_button_menu_actions import AllButtonMenuActions
from .base_panel import BasePanel


class MainWindowPanelLeft(BasePanel):

    class Buttons:
        def __init__(self, buttons: AllButtonMenuActions):
            max_width = 140
            self.start: QPushButton = buttons.START_SIMULATION.button()
            self.pause: QPushButton = buttons.PAUSE_SIMULATION.button()
            self.exit: QPushButton = buttons.EXIT_APP.button()
            self.add_synapsevisual: QPushButton = buttons.ADD_SYNAPSEVISUAL.button()
            self.add_selector_box: QPushButton = buttons.ADD_SELECTOR_BOX.button()
            self.toggle_outergrid: QPushButton = buttons.TOGGLE_OUTERGRID.button()

            self.toggle_outergrid.setMinimumWidth(max_width)
            self.toggle_outergrid.setMaximumWidth(max_width)
            self.start.setMaximumWidth(max_width)
            self.exit.setMaximumWidth(max_width)

    class Sliders:
        def __init__(self, window):

            self.thalamic_inh_input_current = SpinBoxSlider(name='Inhibitory Current [I]',
                                                            window=window,
                                                            status_tip='Thalamic Inhibitory Input Current [I]',
                                                            prop_id='thalamic_inh_input_current',
                                                            maximum_width=300,
                                                            _min_value=0, _max_value=250)

            self.thalamic_exc_input_current = SpinBoxSlider(name='Excitatory Current [I]',
                                                            window=window,
                                                            status_tip='Thalamic Excitatory Input Current [I]',
                                                            prop_id='thalamic_exc_input_current',
                                                            maximum_width=300,
                                                            _min_value=0, _max_value=250)

            self.sensory_input_current0 = SpinBoxSlider(name='Input Current 0 [I]',
                                                        window=window,
                                                        status_tip='Sensory Input Current 0 [I]',
                                                        prop_id='sensory_input_current0',
                                                        maximum_width=300,
                                                        _min_value=0, _max_value=200)

            self.sensory_input_current1 = SpinBoxSlider(name='Input Current 1 [I]',
                                                        window=window,
                                                        status_tip='Sensory Input Current 1 [I]',
                                                        prop_id='sensory_input_current1',
                                                        maximum_width=300,
                                                        _min_value=0, _max_value=200)

            self.sensory_weight = SpinBoxSlider(name='Sensory',
                                                boxlayout_orientation=Qt.Orientation.Horizontal,
                                                window=window,
                                                func_=lambda x: float(x) / 100000 if x is not None else x,
                                                func_inv_=lambda x: int(x * 100000) if x is not None else x,
                                                status_tip='Sensory Weight',
                                                prop_id='src_weight',
                                                maximum_width=300,
                                                single_step_spin_box=0.01,
                                                single_step_slider=100,
                                                _min_value=0, _max_value=5)

    def __init__(self, window, buttons: AllButtonMenuActions,
                 # plotting_config: PlottingConfig
                 ):

        BasePanel.__init__(self, window)

        self.window = window

        self.buttons = self.Buttons(buttons=buttons)
        self.sliders = self.Sliders(window)

        play_pause_widget = QWidget(self)
        play_pause_widget.setFixedSize(95, 45)
        play_pause_hbox = QHBoxLayout(play_pause_widget)
        play_pause_hbox.setContentsMargins(0, 0, 0, 0)
        play_pause_hbox.setSpacing(2)
        play_pause_hbox.addWidget(self.buttons.start)
        play_pause_hbox.addWidget(self.buttons.pause)

        # if plotting_config.windowed_neuron_interfaces is False:
        #     self.neurons_collapsible = NeuronsCollapsible(parent=self)
        # self.chemical_collapsible = ChemicalControlCollapsibleContainer(parent=self)
        # self.synapse_collapsible = SynapseCollapsibleContainer(parent=self)
        # self.synapse_collapsible.add(self.buttons.add_synapsevisual)
        # self.sensory_input_collapsible = CollapsibleWidget(self, title='Sensory Input')
        # self.sensory_input_collapsible.add(self.sliders.sensory_input_current0.widget)
        # self.sensory_input_collapsible.add(self.sliders.sensory_input_current1.widget)
        #
        # self.thalamic_input_collapsible = CollapsibleWidget(self, title='Thalamic Input')
        # self.thalamic_input_collapsible.add(self.sliders.thalamic_inh_input_current.widget)
        # self.thalamic_input_collapsible.add(self.sliders.thalamic_exc_input_current.widget)
        #
        # self.weights_collapsible = CollapsibleWidget(self, title='Weights')
        # self.weights_collapsible.add(self.sliders.sensory_weight.widget)
        #
        # self.objects_collapsible = CollapsibleWidget(self, title='Objects')
        #
        self.addWidget(play_pause_widget)
        self.addWidget(self.buttons.toggle_outergrid)
        # self.addWidget(self.chemical_collapsible)
        # if plotting_config.windowed_neuron_interfaces is False:
        #     self.addWidget(self.neurons_collapsible)
        # self.addWidget(self.synapse_collapsible)
        # self.addWidget(self.weights_collapsible)
        # self.addWidget(self.sensory_input_collapsible)
        # self.addWidget(self.thalamic_input_collapsible)

        self.addWidget(self.buttons.add_selector_box)
        # self.addWidget(self.objects_collapsible)

        self.addWidget(self.buttons.exit)


    # def add_3d_object_sliders(self, obj):
    #     collapsible = RenderedObjectCollapsible(obj, self.window, self)
    #     self.objects_collapsible.add(collapsible)
    #     return collapsible
