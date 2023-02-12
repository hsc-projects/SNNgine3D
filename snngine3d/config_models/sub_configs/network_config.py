from dataclasses import dataclass
import numpy as np
from typing import Optional, Union

import pandas as pd

from snngine3d.config_models.utils import boxed_string
from .chemical_config import ChemicalConfig, ChemicalConfigCollection, DefaultChemicals


class NetworkInitValues:
    @dataclass
    class ThalamicInput:
        inh_current: float = 25.
        exc_current: float = 15.

    @dataclass
    class SensoryInput:
        input_current0: float = 65.
        input_current1: float = 25.

    @dataclass
    class Weights:
        Inh2Exc: float = -.49
        Exc2Inh: float = .75
        Exc2Exc: float = .75
        SensorySource: float = .75

    def __init__(self):
        self.ThalamicInput = self.ThalamicInput()
        self.SensoryInput = self.SensoryInput()
        self.Weights = self.Weights()


@dataclass
class NetworkConfig:

    N: int = 100000
    S: Optional[int] = None
    D: Optional[int] = None
    G: Optional[int] = None
    T: int = 5000  # Max simulation record duration

    pos: np.array = None
    N_pos_shape: tuple = (1, 1, 1)

    vispy_scatter_plot_stride: int = 14  # enforced by the vispy scatterplot memory layout

    location_group_segmentation: tuple = None

    N_G_n_cols: int = 2
    N_G_neuron_type_col: int = 0
    N_G_group_id_col: int = 1

    sensory_groups: Optional[list[int]] = None
    output_groups: Optional[list[int]] = None

    max_z: float = 999.

    sim_updates_per_frame: Optional[int] = None

    debug: bool = False

    stdp_active: bool = False

    max_n_winner_take_all_layers: int = 20
    max_winner_take_all_layer_size: int = 10

    InitValues: NetworkInitValues = NetworkInitValues()

    chemical_configs: Optional[Union[list[ChemicalConfig],
                                     ChemicalConfig,
                                     ChemicalConfigCollection,
                                     DefaultChemicals]] = None

    def __str__(self):
        name = self.__class__.__name__
        msg = boxed_string(name)
        msg += f'\n\tN={self.N}, \n\tS={self.S}, \n\tD={self.D}, \n\tG={self.G},'
        msg += f'\n\tN_pos_shape={self.N_pos_shape},'
        msg += f'\n\tgrid_segmentation={self.location_group_segmentation}'
        return msg

    def __post_init__(self):

        assert self.N % 2 == 0

        if self.N <= 4000:
            self.N_pos_shape = (1, 1, 1)

        if self.sim_updates_per_frame is None:
            if self.N <= 10 ** 5:
                self.sim_updates_per_frame = 1
            elif self.N <= 40 ** 5:
                self.sim_updates_per_frame = 5
            else:
                self.sim_updates_per_frame = 10

        if self.S is None:
            self.S = int(min(1000, max(np.sqrt(self.N) + 50, 2)))
        if self.D is None:
            self.D = min(int(max(np.log10(self.N) * (1 + np.sqrt(np.log10(self.N))), 2)), 20)

        # assert self.N >= 20
        # assert self.N <= 2 * 10 ** 6
        assert isinstance(self.N, int)
        assert self.S <= 1000
        assert isinstance(self.S, int)
        assert self.D <= 100
        assert isinstance(self.D, int)
        assert len(self.N_pos_shape) == 3
        # assert self.is_cube
        # assert self.shape[0] == 1
        min_shape_el = min(self.N_pos_shape)
        assert all([
            isinstance(s, int) and (s / min_shape_el == int(s / min_shape_el)) for s in self.N_pos_shape
        ])
        assert self.vispy_scatter_plot_stride == 14  # enforced by the vispy scatterplot memory layout

        self.swap_tensor_shape_multiplicators: tuple = (self.S, 10)

        if self.chemical_configs is not None:
            if not isinstance(self.chemical_configs, ChemicalConfigCollection):
                chemical_configs = self.chemical_configs
                if not isinstance(self.chemical_configs, list):
                    chemical_configs = [self.chemical_configs]
                names = []
                for chem in chemical_configs:
                    assert isinstance(chem, ChemicalConfig)
                    names.append(chem.name)
                assert not bool(pd.Series(names).duplicated().any())
                self.chemical_configs = ChemicalConfigCollection()
                for chem in chemical_configs:
                    setattr(self.chemical_configs, chem.name, chem)

        self.location_group_segmentation = self._segmentation(self.location_group_segmentation)

        self.G = (self.location_group_segmentation[0]
                  * self.location_group_segmentation[1]
                  * self.location_group_segmentation[2])

    def _segmentation(self, grid_segmentation):
        if grid_segmentation is None:
            segmentation_list = []
            for s in self.N_pos_shape:
                f = max(self.N_pos_shape) / min(self.N_pos_shape)
                segmentation_list.append(
                    int(int(max(self.D / (np.sqrt(3) * f), 2)) * (s / min(self.N_pos_shape))))
            grid_segmentation = tuple(segmentation_list)
        min_g_shape = min(grid_segmentation)
        assert all([isinstance(s, int)
                    and (s / min_g_shape == int(s / min_g_shape)) for s in grid_segmentation])
        return grid_segmentation
