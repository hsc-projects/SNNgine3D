from dataclasses import dataclass
from typing import Optional, Union


from .network_config import NetworkConfig


@dataclass(frozen=True)
class PlotViewModeOption:

    mode: str

    def __post_init__(self):
        view_modes = ['scene', 'windowed', 'split']
        assert self.mode in view_modes

    def __eq__(self, other):
        return self.mode == other

    @property
    def scene(self):
        return self.mode == 'scene'

    @property
    def split(self):
        return self.mode == 'split'

    @property
    def windowed(self):
        return self.mode == 'windowed'


@dataclass
class PlottingConfig:

    n_voltage_plots: int
    voltage_plot_length: int

    n_scatter_plots: int
    scatter_plot_length: int

    network_config: NetworkConfig

    has_voltage_multiplot: bool = True
    has_firing_scatterplot: bool = True
    has_group_firings_multiplot: bool = True
    has_group_firings_plot0: bool = True
    has_group_firings_plot1: bool = True

    windowed_multi_neuron_plots: bool = True
    windowed_neuron_interfaces: bool = True
    group_info_view_mode: Optional[Union[PlotViewModeOption, str]] = 'split'

    _max_length: int = 10000
    _max_n_voltage_plots: int = 1000
    _max_n_scatter_plots: int = 1000

    def __post_init__(self):

        if self.windowed_multi_neuron_plots is True:
            assert self.has_voltage_multiplot
            assert self.has_firing_scatterplot

        if isinstance(self.group_info_view_mode, str):
            self.group_info_view_mode = PlotViewModeOption(self.group_info_view_mode)
        elif not isinstance(self.group_info_view_mode, PlotViewModeOption):
            raise TypeError

        self.n_voltage_plots = min(min(self.N, self.n_voltage_plots), self._max_n_voltage_plots)
        self.n_scatter_plots = min(min(self.N, self.n_scatter_plots), self._max_n_scatter_plots)
        self.voltage_plot_length = min(self.voltage_plot_length, self._max_length)
        self.scatter_plot_length = min(self.scatter_plot_length, self._max_length)

    # noinspection PyPep8Naming
    @property
    def N(self):
        return self.network_config.N

    # noinspection PyPep8Naming
    @property
    def G(self):
        return self.network_config.G
