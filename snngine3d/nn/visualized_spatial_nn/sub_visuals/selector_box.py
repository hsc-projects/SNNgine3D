import numpy as np
import torch
from typing import Optional

from vispy.visuals.transforms import STTransform

from snngine3d.config_models import NetworkConfig
# from network.network_state.location_group_states import (
#     LocationGroupFlags,
#     LocationGroupProperties
# )
# TODO: remove


class LocationGroupFlags:
    pass


class LocationGroupProperties:
    pass


from snngine3d.vispy_torch_interop import (
    CudaBox,
    CudaGridArrow,
    RenderedCudaObjectNode,
    Scale,
    Translate
)
from snngine3d.nn.grid import NetworkGrid


# noinspection PyAbstractClass
class SelectorBox(RenderedCudaObjectNode):
    count: int = 0

    def __init__(self,
                 scene, view,
                 network_config: NetworkConfig, grid: NetworkGrid,
                 device, G_flags: LocationGroupFlags, G_props: LocationGroupProperties,
                 parent=None, name=None):
        scene.set_current()
        self.name = name or f'{self.__class__.__name__}{SelectorBox.count}'

        self._select_children: list[CudaGridArrow] = []

        self.network_config = network_config
        self.grid = grid
        self.original_color = (1, 0.65, 0, 0.5)
        self._visual: CudaBox = CudaBox(select_parent=self,
                                        name=self.name + '.obj',
                                        shape=self.shape,
                                        # color=np.array([1, 0.65, 0, 0.5]),
                                        color=(1, 0.65, 0, 0.1),
                                        edge_color=self.original_color,
                                        # scale=[1.1, 1.1, 1.1],
                                        depth_test=False,
                                        border_width=2,
                                        parent=None)

        super().__init__([self._visual], selectable=True, parent=parent)

        self.unfreeze()
        self._scene = scene
        self.transform = STTransform()
        self.transform.translate = (self.shape[0] / 2, self.shape[1] / 2, self.shape[2] / 2)
        self.transform.scale = [1.1, 1.1, 1.1]

        self._visual.normals.transform = self.transform

        SelectorBox.count += 1
        self.interactive = True
        self.scale = Scale(self, _min_value=0, _max_value=int(3 * 1 / min(self.shape)))
        self.translate = Translate(self, _grid_unit_shape=self.shape, _min_value=-5, _max_value=5)
        self.map_window_keys()

        self.G_flags: Optional[LocationGroupFlags] = None
        self.G_props: Optional[LocationGroupProperties] = None

        # noinspection PyPep8Naming
        self.selected_masks = np.zeros((self.network_config.G, 4), dtype=np.int32, )

        self.group_numbers = np.arange(self.network_config.G)  # .reshape((G, 1))

        self.selection_flag = 'b_thalamic_input'

        self.freeze()

        view.add(self)
        scene._draw_scene()
        self.init_cuda_attributes(device=device, G_flags=G_flags, G_props=G_props)

    @property
    def parent(self):
        return super().parent

    @parent.setter
    def parent(self, value):
        super(RenderedCudaObjectNode, self.__class__).parent.fset(self, value)
        for o in self.visual.normals:
            o.parent = value

    @property
    def g_pos(self):
        return self.grid.pos[:self.network_config.G, :]

    @property
    def g_pos_end(self):
        return self.grid.pos_end[:self.network_config.G, :]

    @property
    def shape(self):
        return self.grid.unit_shape

    @property
    def color(self):
        return self.visual._border.color

    @color.setter
    def color(self, v):
        self.visual._border.color = v

    @property
    def vbo_glir_id(self):
        return self.visual._border._vertices.id

    @property
    def selection_vertices(self):
        return (self.visual._initial_selection_vertices
                * self.transform.scale[:3]
                + self.transform.translate[:3])

    @property
    def edge_lengths(self):
        return np.array(self.shape) * self.transform.scale[:3]

    def transform_changed(self):
        g_pos = self.g_pos
        g_pos_end = self.g_pos_end
        v = self.selection_vertices
        self.selected_masks[:, 0] = (g_pos[:, 0] >= v[0, 0]) & (g_pos_end[:, 0] <= v[1, 0])
        self.selected_masks[:, 1] = (g_pos[:, 1] >= v[0, 1]) & (g_pos_end[:, 1] <= v[2, 1])
        self.selected_masks[:, 2] = (g_pos[:, 2] >= v[0, 2]) & (g_pos_end[:, 2] <= v[3, 2])
        mask = torch.from_numpy(self.selected_masks[:, :3].all(axis=1)).to(self._cuda_device)
        # TODO: uncomment
        # self.G_flags.selected = mask
        # if self.selection_flag is not None:
        #     setattr(self.G_flags, self.selection_flag, mask)

    def on_select_callback(self, v: bool):
        self.swap_select_color(v)
        self._visual.normals.visible = v

        if v is True:
            self.map_window_keys()

    # noinspection PyMethodOverriding
    def init_cuda_attributes(self, device, G_flags: LocationGroupFlags, G_props: LocationGroupProperties):
        super().init_cuda_attributes(device)
        self.G_flags = G_flags
        self.G_props = G_props
        self.transform_connected = True
        self._visual.normals.visible = False

        for normal in self._visual.normals:
            self.registered_buffers.append(normal.gpu_array)

    def map_window_keys(self):
        self._scene.events.key_press.disconnect()
        self._scene.set_keys({
            'left': self.translate.mv_left,
            'right': self.translate.mv_right,
            'up': self.translate.mv_fw,
            'down': self.translate.mv_bw,
            'pageup': self.translate.mv_up,
            'pagedown': self.translate.mv_down,
        })
