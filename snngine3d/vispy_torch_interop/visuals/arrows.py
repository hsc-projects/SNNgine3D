from typing import Optional

import numpy as np
from vispy.scene import visuals, Node

from snngine3d.vispy_torch_interop.rendered_objects import RenderedCudaObject, RenderedCudaObjectNode
from snngine3d.geometry.grid import GridDirectionsObject, box_normal_origins
from snngine3d.geometry.vector import CursorDragResult2D, Segment2DArray, Segment3DArray, Segment4DArrayCanvas


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

    def __init__(self, select_parent, points: np.ndarray, color=None, name=None, tube_points=4,
                 radius=np.array([.012, .012, .05, .0]), parent: Optional[Node] = None,
                 selectable=True, draggable=True, mod_factor=1):

        if points.shape[1] != 3:
            raise TypeError

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

        self._initial_seg = Segment3DArray(np.array([np.array([0, 0, 0]), self._points[0]]))
        self._seg_canvas_4d = Segment4DArrayCanvas()
        self._seg_scene = Segment3DArray()
        self._drag_result = CursorDragResult2D()

        # self._canvas_length = None
        self._visual = CudaArrowVisual(points=points,
                                       name=name + '.obj',
                                       parent=None,
                                       tube_points=tube_points, radius=radius, color=color)

        super().__init__([self._visual], parent=parent, selectable=selectable, name=name, draggable=draggable)
        self.interactive = True

    @property
    def seg_scene(self) -> Segment3DArray:
        # return Segment3D.from_numpy(self.get_transform('visual', 'scene').map(self._initial_line_seg_repr_np))
        return self._seg_scene.set_array(self.get_transform('visual', 'scene').map(self._initial_seg.array)[:, :3])

    @property
    def seg_canvas(self) -> Segment4DArrayCanvas:
        return self._seg_canvas_4d.set_array(self.get_transform('visual', 'canvas').map(self._initial_seg.array))

    def actualize_ui(self):
        getattr(self.select_parent.scale.spin_box_sliders, self._dim).actualize_values()
        getattr(self.select_parent.translate.spin_box_sliders, self._dim).actualize_values()

    @property
    def color_vbo_glir_id(self):
        return self._visual.shared_program.vert['base_color'].id

    def init_cuda_arrays(self):
        self._gpu_array = self.face_color_array(buffer=self.color_vbo, mesh_data=self.visual.mesh_data)

    def on_drag_callback(self, drag: Segment2DArray, mode: int):
        factor = self._drag_result.update(dragged_seg=self.seg_canvas.segment2d, drag_seg=drag).factor
        if factor == 1:
            return

        prev_canvas_seg4d_0 = self.seg_canvas
        prev_canvas_seg2d_0 = prev_canvas_seg4d_0.segment2d
        line_scene = self.seg_scene
        new_canvas_target = self._drag_result.target()

        vector_4d = prev_canvas_seg4d_0.to_vector()

        new_vec4 = Segment4DArrayCanvas.from_vector(
            vector=vector_4d * factor, source=prev_canvas_seg4d_0.source())
        prev_canvas_seg2d_1 = new_vec4.segment2d
        # effect only in one direction w.r.t. the canvas (up/down or left/right]
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
