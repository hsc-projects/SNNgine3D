from typing import Optional

import numpy as np
from vispy.scene import visuals, Node

from snngine3d.vispy_torch_interop.rendered_objects import RenderedCudaObject, RenderedCudaObjectNode
from snngine3d.geometry.grid import GridDirectionsObject, initial_normal_vertices
from snngine3d.geometry.vector import segment_intersection2d


class CudaArrowVisual(visuals.Tube, RenderedCudaObject):

    def __init__(self, points, color=None, name=None, parent: Optional[Node] = None,
                 tube_points=4, radius=np.array([.01, .01, .025, .0])):

        self._points = points
        self._tube_points = tube_points

        visuals.Tube.__init__(self, name=name, points=points, tube_points=tube_points, radius=radius,
                              color=color,
                              parent=parent)
        RenderedCudaObject.__init__(self)

    # def on_mouse_press(self, event):
    #     self.print_mouse_event(event, 'Mouse press')
    #     pos_scene = event.pos[:3]


# noinspection PyAbstractClass
class CudaGridArrow(RenderedCudaObjectNode):

    def __init__(self, select_parent, points, color=None, name=None, tube_points=4,
                 radius=np.array([.012, .012, .05, .0]), parent: Optional[Node] = None,
                 selectable=True, draggable=True, mod_factor=1):

        self.last_scale = None
        self.last_translate = None

        self._mod_factor = mod_factor

        self.select_parent = select_parent
        self._translate_dir = 1
        for i, d in enumerate(['x', 'y', 'z']):
            if (points[:, i] != 0).any():
                self._dim_int = i
                self._dim: str = d
                self._translate_dir = 1
                self._modifier_dir = 1
                if (points[:, i] < 0).any():
                    self._modifier_dir = -1
                    self._translate_dir = -1

        self._modifier_dim = 0
        if self._dim == 'z':
            self._modifier_dim = 1
            self._modifier_dir *= -1
            # self._translate_dir *= -1

        self.default_alpha = .5

        if name is None:
            name = (f"{self._select_parent.name}.{self.__class__.__name__}:{self._dim}"
                    f"{'+' if self._modifier_dir > 0 else '-'}")

        if color is None:
            if points[:, 0].any():
                color = np.array([1., 0., 0., self.default_alpha], dtype=np.float32)
            elif points[:, 1].any():
                color = np.array([0., 1., 0., self.default_alpha], dtype=np.float32)
            else:
                color = np.array([0., 0., 1., self.default_alpha], dtype=np.float32)
        self._points = points
        # self._canvas_length = None
        self._visual = CudaArrowVisual(points=points,
                                       name=name + '.obj',
                                       parent=None,
                                       tube_points=tube_points, radius=radius, color=color)

        super().__init__([self._visual], parent=parent, selectable=selectable, name=name, draggable=draggable)
        self.interactive = True

    def on_select_callback(self, v):
        # print(f'\nselected arrow({v}):', self, '\n')
        self.gpu_array.tensor[:, 3] = 1. if v is True else self.default_alpha

        self.last_scale = getattr(self.select_parent.scale, self._dim)
        self.last_translate = getattr(self.select_parent.translate, self._dim)

    def on_drag_callback(self, old_pos: np.ndarray, new_pos: np.ndarray, mode: int):

        p0 = self.get_transform('visual', 'canvas').map(self._points[0])
        p1 = self.get_transform('visual', 'canvas').map(self._points[-1])

        p0_canvas = p0[:2]/p0[3]
        p1_canvas = p1[:2]/p1[3]

        diff = new_pos - old_pos
        p_drag = p1_canvas + diff

        p_drag_hline = np.array([p_drag, p_drag + np.array([1, 0])])
        p_drag_vline = np.array([p_drag, p_drag + np.array([0, 1])])

        # new_hline_intersect = np.empty_like(p0)
        p_drag_hline_intersect = segment_intersection2d(
            seg0=np.array([p0_canvas, p1_canvas]),
            seg1=p_drag_hline,
        )
        p_drag_vline_intersect = segment_intersection2d(
            seg0=np.array([p0_canvas, p1_canvas]),
            seg1=p_drag_vline,
        )

        # hline_dist = np.linalg.norm(p_drag_hline_intersect - p1_canvas)
        # vline_dist = np.linalg.norm(p_drag_vline_intersect - p1_canvas)
        #
        # new_p1_canvas = p_drag_vline_intersect if vline_dist > hline_dist else p_drag_hline_intersect
        #
        # old_length = np.linalg.norm(p1_canvas - p0_canvas)
        # new_length = np.linalg.norm(new_p1_canvas - p0_canvas)
        #
        # v = (new_length / old_length) * self._modifier_dir
        #
        # if np.isnan(v):
        #     print()
        #
        # print(v)

        if mode == 0:
            setattr(self.select_parent.scale, self._dim, self.last_scale * v/2)
        elif mode == 1:
            setattr(self.select_parent.translate, self._dim,
                    self.last_translate * v/4)
        else:
            new_scale = self.last_scale * v/2
            setattr(self.select_parent.scale, self._dim, new_scale)
            edge_diff = self.select_parent.shape[self._dim_int] * (new_scale - self.last_scale)
            setattr(self.select_parent.translate, self._dim,
                    self.last_translate + self._translate_dir * (edge_diff / 2))
        self.actualize_ui()

    def actualize_ui(self):
        getattr(self.select_parent.scale.spin_box_sliders, self._dim).actualize_values()
        getattr(self.select_parent.translate.spin_box_sliders, self._dim).actualize_values()

    @property
    def pos_vbo_glir_id(self):
        return self._visual._vertices.id

    @property
    def color_vbo_glir_id(self):
        return self._visual.shared_program.vert['base_color'].id

    def init_cuda_arrays(self):
        self._gpu_array = self.face_color_array(buffer=self.color_vbo, mesh_data=self.visual.mesh_data)


class InteractiveBoxNormals(GridDirectionsObject):

    def __init__(self, select_parent, shape, mod_factors=None):

        normals = []
        inv = initial_normal_vertices(shape)
        for i in range(6):
            if mod_factors is None:
                mod_factor = 1 / (3 * shape[int(i / 2)])
            else:
                mod_factor = mod_factors[i]
            arrow = CudaGridArrow(select_parent, points=inv[i], mod_factor=mod_factor)
            normals.append(arrow)
        super().__init__(obj=normals)

    @property
    def visible(self):
        return self[0].visible

    @visible.setter
    def visible(self, value):
        for i in self:
            i.visible = value

    @property
    def transform(self):
        return self[0].transform

    @transform.setter
    def transform(self, value):
        for i in self:
            i.transform = value
