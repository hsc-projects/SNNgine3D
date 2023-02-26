from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow
from typing import Optional

from snngine3d.engine.widgets import (
    ButtonMenuAction,
    SpinBoxSlider
)
from snngine3d.engine.widgets.collapsibles import (
    CollapsibleWidget,
    NeuronIDFrame
)

# TODO: remove
class SpikingNeuralNetwork:
    pass


class VisualizedSynapsesCollection:
    pass


class SynapticWeightsCollapsible(CollapsibleWidget):

    class Sliders:
        def __init__(self, window: QMainWindow):

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

    def __init__(self, parent, window):

        super().__init__(parent=parent, title='Weights')

        self.sliders = self.Sliders(window)
        self.add(self.sliders.sensory_weight.widget)


class SynapseCollapsible(CollapsibleWidget):

    def __init__(self, parent, network: SpikingNeuralNetwork,
                 title, neuron_id):

        super().__init__(parent=parent, title=title)

        self.id_frame = NeuronIDFrame(self, network.network_config.N)
        self.id_frame.spinbox.setValue(neuron_id)

        self.id_frame.spinbox.valueChanged.connect(self.update_neuron_id)

        self._last_id = neuron_id
        self.visual_collection: Optional[VisualizedSynapsesCollection] = network.synapse_arrays.visualized_synapses

        self.add(self.id_frame)

        self.visual_collection.add_synapse_visual(neuron_id=neuron_id)

    def update_neuron_id(self):
        new_id = self.id_frame.spinbox.value()
        self.visual_collection.move_visual(prev_neuron_id=self._last_id, new_neuron_id=new_id)
        self._last_id = new_id

    @property
    def visual(self):
        return self.visual_collection._dct[self.id_frame.spinbox.value()]


class SynapseCollectionCollapsible(CollapsibleWidget):

    def __init__(self, window: QMainWindow, title='Visualized Synapses', parent=None):
        CollapsibleWidget.__init__(self, title=title, parent=parent)

        self.ADD_SYNAPSE_VISUAL: ButtonMenuAction = ButtonMenuAction(
            menu_name='&Add SynapseVisual',
            name='Add SynapseVisual',
            status_tip='Add SynapseVisual',
            window=window)
        self.add(self.ADD_SYNAPSE_VISUAL.button())
        self.interfaced_synapses_dct = {}

    def add_interfaced_synapse(self, network: SpikingNeuralNetwork, neuron_id: int, title=None):

        index = len(self.interfaced_synapses_list)

        if title is None:
            title = 'VisualizedSynapses' + str(index)

        syn_collapsible = SynapseCollapsible(self, network=network, title=title, neuron_id=neuron_id)

        self.interfaced_synapses_dct[title] = syn_collapsible

        self.add(syn_collapsible)
        self.toggle_collapsed()
        self.toggle_collapsed()

        return syn_collapsible

    @property
    def interfaced_synapses_list(self):
        return list(self.interfaced_synapses_dct.values())
