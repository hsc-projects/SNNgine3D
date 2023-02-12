from dataclasses import dataclass
# from typing import Type

from snngine3d.config_models import (
    NetworkInitValues,
    NetworkConfig,
    PlottingConfig,
    DefaultChemicals
)


class EngineConfig:

    class InitValues(NetworkInitValues):

        @dataclass
        class ThalamicInput:
            inh_current: float = 25.
            exc_current: float = 15.

        @dataclass
        class SensoryInput:
            input_current0: float = 22.3
            input_current1: float = 42.8

        @dataclass
        class Weights:
            Inh2Exc: float = -.49
            Exc2Inh: float = .75
            Exc2Exc: float = .75
            SensorySource: float = 1.5

    device: int = 0

    max_batch_size_mb: int = 300

    network = NetworkConfig(N=25 * 10 ** 3,
                            T=5000,
                            N_pos_shape=(4, 4, 1),
                            sim_updates_per_frame=1,
                            stdp_active=True,
                            debug=False, InitValues=InitValues(),
                            chemical_configs=DefaultChemicals())
    plotting = PlottingConfig(n_voltage_plots=10, voltage_plot_length=200,
                              n_scatter_plots=10, scatter_plot_length=200,
                              has_voltage_multiplot=True,
                              has_firing_scatterplot=True,
                              has_group_firings_multiplot=False,
                              has_group_firings_plot0=True,
                              has_group_firings_plot1=True,
                              windowed_multi_neuron_plots=False,
                              windowed_neuron_interfaces=False,
                              group_info_view_mode='split',
                              network_config=network)

    # network_class: Type[SpikingNeuralNetwork] = None
    update_single_neuron_plots: bool = False

    screen: int = 0
