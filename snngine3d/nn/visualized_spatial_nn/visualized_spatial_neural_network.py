import numpy as np
from typing import Dict, Optional, Union

from snngine3d.nn.grid import NetworkGrid
from snngine3d.config_models import (
    EngineConfig,
    NetworkConfig,
    PlottingConfig
)
from .sub_visuals import SelectorBox
from snngine3d.vispy_torch_interop.utils import TorchCollection


class PseudoNs:
    G_flags = None
    G_props = None


class VisualizedSpatialNeuralNetwork(TorchCollection):

    def __init__(self, engine):

        eng_conf: EngineConfig = engine.config
        self.nn_conf: NetworkConfig = eng_conf.network
        self.plot_conf: PlottingConfig = eng_conf.plotting

        self.grid = NetworkGrid(config=self.nn_conf)

        super().__init__(eng_conf.device)

        self.neurons = PseudoNs()

    def add_selector_box(self, scene, view):
        selector_box = SelectorBox(scene, view, self.nn_conf, self.grid,
                                   self.device,
                                   self.neurons.G_flags, self.neurons.G_props)
        self.registered_buffers += selector_box.registered_buffers
        return selector_box

    def unregister_registered_buffers(self):
        for rb in self.registered_buffers:
            rb.unregister()
        self.synapse_arrays.unregister_registered_buffers()
