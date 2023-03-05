from typing import Optional

import numpy as np
from vispy.scene import visuals, Node

from snngine3d.vispy_torch_interop.rendered_objects import RenderedCudaObject, RenderedCudaObjectNode
from snngine3d.geometry.grid import GridDirectionsObject, box_normal_origins
from snngine3d.geometry.vector import LineSegment, segment_intersection2d


class CudaArrowVisual(visuals.Tube, RenderedCudaObject):

    def __init__(self, points, color=None, name=None, parent: Optional[Node] = None,
                 tube_points=4, radius=np.array([.01, .01, .025, .0])):

        self._points = points
        self._tube_points = tube_points

        visuals.Tube.__init__(self, name=name, points=points, tube_points=tube_points, radius=radius,
                              color=color,
                              parent=parent)
        RenderedCudaObject.__init__(self)


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

        self.validate_initial_vertices(points)

        for i, d in enumerate(['x', 'y', 'z']):
            if bool((points[:, i] != 0).any()):
                self._dim_int = i
                self._dim: str = d
                self._translate_dir = 1
                self._modifier_dir = 1
                if bool((points[:, i] < 0).any()):
                    self._modifier_dir = -1
                    self._translate_dir = -1

        self._modifier_dim = 0
        if self._dim == 'z':
            self._modifier_dim = 1
            self._modifier_dir *= -1
            # self._translate_dir *= -1

        self._default_alpha = .5

        if name is None:
            name = (f"{self._select_parent.name}.{self.__class__.__name__}:{self._dim}"
                    f"{'+' if self._modifier_dir > 0 else '-'}")

        if color is None:
            if self._dim == 'x':
                color = np.array([1., 0., 0., self._default_alpha], dtype=np.float32)
            elif self._dim == 'y':
                color = np.array([0., 1., 0., self._default_alpha], dtype=np.float32)
            else:
                if self._dim != 'z':
                    raise AttributeError
                color = np.array([0., 0., 1., self._default_alpha], dtype=np.float32)
        self._points = points

        self._initial_line_seg_repr = LineSegment(
            p_start=np.array([0, 0, 0]),
            p_end=np.array(self._points[0])
        )
        self._line_seg_repr_canvas: Optional[LineSegment] = None
        self._line_seg_repr_canvas_tmp: Optional[LineSegment] = None
        self._line_seg_repr_scene: Optional[LineSegment] = None
        self._cross_line_h_end: np.ndarray = np.array([1, 0])
        self._cross_line_h: LineSegment = LineSegment(p_start=np.array([0, 0]), p_end=self._cross_line_h_end)
        self._cross_line_v_end: np.ndarray = np.array([0, 1])
        self._cross_line_v: LineSegment = LineSegment(p_start=np.array([0, 0]), p_end=self._cross_line_v_end)

        # self._canvas_length = None
        self._visual = CudaArrowVisual(points=points,
                                       name=name + '.obj',
                                       parent=None,
                                       tube_points=tube_points, radius=radius, color=color)

        super().__init__([self._visual], parent=parent, selectable=selectable, name=name, draggable=draggable)
        self.interactive = True

    @property
    def line_seg_repr_scene(self) -> LineSegment:
        new_points = self.get_transform('visual', 'scene').map(self._initial_line_seg_repr.array)
        if self._line_seg_repr_scene is not None:
            self._line_seg_repr_scene.set_points(new_points)
        else:
            self._line_seg_repr_scene = LineSegment.from_array(new_points)
        return self._line_seg_repr_scene

    @property
    def line_seg_repr_canvas(self) -> LineSegment:
        new_points_ = self.get_transform('visual', 'canvas').map(self._initial_line_seg_repr.array)
        new_points = np.empty_like(new_points_[:, :2])
        new_points[0][:] = new_points_[0][:2] / new_points_[0][3]
        new_points[1][:] = new_points_[1][:2] / new_points_[1][3]
        if self._line_seg_repr_canvas is not None:
            self._line_seg_repr_canvas.set_points(new_points)
        else:
            self._line_seg_repr_canvas = LineSegment.from_array(new_points)
        return self._line_seg_repr_canvas

    def actualize_ui(self):
        getattr(self.select_parent.scale.spin_box_sliders, self._dim).actualize_values()
        getattr(self.select_parent.translate.spin_box_sliders, self._dim).actualize_values()

    @property
    def color_vbo_glir_id(self):
        return self._visual.shared_program.vert['base_color'].id

    def init_cuda_arrays(self):
        self._gpu_array = self.face_color_array(buffer=self.color_vbo, mesh_data=self.visual.mesh_data)

    def on_drag_callback(self, drag: LineSegment, mode: int):

        canvas_line = self.line_seg_repr_canvas

        drag_dim = np.argmax(canvas_line.vec)
        p_drag = canvas_line.p_end + drag.vec
        if drag_dim == 0:
            # self._cross_line_v.array = self._cross_line_v.array + canvas_line.p_end + drag
            self._cross_line_v.set_p_start(p_drag)
            self._cross_line_v.set_p_end(self._cross_line_v_end + p_drag)
            cross_line = self._cross_line_v
        else:
            self._cross_line_h.set_p_start(p_drag)
            self._cross_line_h.set_p_end(self._cross_line_h_end + p_drag)
            cross_line = self._cross_line_h

        p_cross = segment_intersection2d(canvas_line, cross_line)

        canvas_line_dir = -1 if canvas_line.p_start[drag_dim] > canvas_line.p_end[drag_dim] else 1
        drag_dir = -1 if drag.p_start[drag_dim] > drag.p_end[drag_dim] else 1

        mod_dir = canvas_line_dir * drag_dir

        self._line_seg_repr_canvas_tmp.set_p_start(canvas_line.p_start)
        self._line_seg_repr_canvas_tmp.set_p_end(canvas_line.p_end)


        mod_factor =

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

        # if mode == 0:
        #     setattr(self.select_parent.scale, self._dim, self.last_scale * v/2)
        # elif mode == 1:
        #     setattr(self.select_parent.translate, self._dim,
        #             self.last_translate * v/4)
        # else:
        #     new_scale = self.last_scale * v/2
        #     setattr(self.select_parent.scale, self._dim, new_scale)
        #     edge_diff = self.select_parent.shape[self._dim_int] * (new_scale - self.last_scale)
        #     setattr(self.select_parent.translate, self._dim,
        #             self.last_translate + self._translate_dir * (edge_diff / 2))
        self.actualize_ui()

    def on_select_callback(self, v):
        # print(f'\nselected arrow({v}):', self, '\n')
        self.gpu_array.tensor[:, 3] = 1. if v is True else self._default_alpha

        self.last_scale = getattr(self.select_parent.scale, self._dim)
        self.last_translate = getattr(self.select_parent.translate, self._dim)

    @property
    def pos_vbo_glir_id(self):
        return self._visual._vertices.id

    @classmethod
    def validate_initial_vertices(cls, vert: np.ndarray):
        if vert.shape[1] != 3:
            raise ValueError

        for i in range(vert.shape[1]):
            if bool((vert[:, i] != 0).any()):
                if bool((vert[:, i-1] != 0).any()) or bool((vert[:, i-2] != 0).any()):
                    raise AttributeError
                break

        distance_from_origin = np.linalg.norm(vert[0])
        for i in range(vert.shape[0] - 1):
            if np.linalg.norm(vert[i + 1]) < distance_from_origin:
                raise ValueError(f"{np.linalg.norm(vert[i + 1])} < {distance_from_origin} (distance_from_origin)")


class InteractiveBoxNormals(GridDirectionsObject):

    def __init__(self, select_parent, shape, mod_factors=None):

        normals = []
        inv = box_normal_origins(shape)
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
