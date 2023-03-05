from typing import Optional, Union

import numpy as np
from vispy.visuals import CompoundVisual
from vispy.scene import visuals
from vispy.gloo.context import get_current_canvas

from snngine3d.geometry.vector import LineSegment
# from snngine3d.vispy_torch_interop.transformation.STR import Scale, Translate


def get_buffer_id(glir_id):
    return int(get_current_canvas().context.shared.parser._objects[glir_id].handle)


class RenderedObject:
    def __init__(self, select_parent=None, selectable=False, draggable=False):

        if not hasattr(self, '_visual'):
            self._visual = None

        if select_parent is not None:
            self.select_parent = select_parent
        if not hasattr(self, '_select_children'):
            self._select_children = []
        if not hasattr(self, '_select_parent'):
            self._select_parent = None
        if not hasattr(self, 'original_color'):
            self.original_color = None
        if not hasattr(self, '_shape'):
            self._shape = None
        if not hasattr(self, 'grid'):
            self.grid = None

        self._vbo = None
        self._pos_vbo = None
        self._color_vbo = None
        self._ibo = None
        # self._parent = None
        self._glir = None

        self.transform_connected = False

        self.selectable = selectable
        self.draggable = draggable
        self.selected = False
        self.select_color = 'white'
        self._color = None
        self.color = self.original_color

        self._cuda_device: Optional[Union[int, str]] = None
        self.scale = None
        self.translate = None
        # self.scale: Optional[Scale] = None
        # self.translate: Optional[Translate] = None
        self._transform = None

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, v):
        self._color = v

    def swap_select_color(self, v):
        if v is True:
            self.color = self.select_color
        else:
            self.color = self.original_color

    @property
    def select_parent(self):
        return self._select_parent

    @select_parent.setter
    def select_parent(self, v):
        self._select_parent = v
        if v is not None:
            v._select_children.append(self)

    def is_select_child(self, v):
        return v in self._select_children

    @property
    def unique_vertices_cpu(self):
        raise NotImplementedError

    @property
    def visual(self):
        return self._visual

    @property
    def glir(self):
        if self._glir is None:
            self._glir = get_current_canvas().context.glir
        return self._glir

    @property
    def shape(self):
        return self._shape

    @property
    def color_vbo_glir_id(self):
        raise NotImplementedError

    @property
    def pos_vbo_glir_id(self):
        return self.vbo_glir_id

    @property
    def ibo_glir_id(self):
        raise NotImplementedError

    @property
    def vbo_glir_id(self):
        raise NotImplementedError

    def transform_changed(self):
        pass

    @staticmethod
    def buffer_id(glir_id):
        return int(get_current_canvas().context.shared.parser._objects[glir_id].handle)

    @property
    def color_vbo(self):
        # print(self.buffer_id(self.color_vbo_glir_id))
        # return self.buffer_id(self.color_vbo_glir_id)
        if self._color_vbo is None:
            self._color_vbo = self.buffer_id(self.color_vbo_glir_id)
        return self._color_vbo

    @property
    def pos_vbo(self):
        if self._pos_vbo is None:
            self._pos_vbo = self.buffer_id(self.pos_vbo_glir_id)
        return self._pos_vbo

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = self.buffer_id(self.vbo_glir_id)
        return self._vbo

    @property
    def ibo(self):
        if self._ibo is None:
            self._ibo = self.buffer_id(self.ibo_glir_id)
        return self._ibo

    def on_select_callback(self, v: bool):
        raise NotImplementedError

    def on_drag_callback(self, drag: LineSegment, mode: int):
        raise NotImplementedError

    def select(self, v):
        if self.selectable is True:
            self.selected = v
            self.on_select_callback(v)

    def update(self):
        self.visual.update()


# noinspection PyAbstractClass
class RenderedObjectVisual(CompoundVisual, RenderedObject):

    def __init__(self, subvisuals, parent=None, selectable=False, draggable=False):

        self.unfreeze()
        RenderedObject.__init__(self, selectable=selectable, draggable=draggable)
        CompoundVisual.__init__(self, subvisuals)
        self.freeze()

        if parent is not None:
            self.parent = parent


# def add_children(parent: Node, children: list):
#     for child in children:
#         parent._add_child(child)


# noinspection PyAbstractClass
class RenderedObjectNode(visuals.VisualNode, RenderedObjectVisual):

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        name = kwargs.pop('name', None)
        if not hasattr(self, 'name'):
            self.name = name  # to allow __str__ before Node.__init__
        self._visual_superclass = RenderedObjectVisual
        RenderedObjectVisual.__init__(self, *args, **kwargs)
        self.unfreeze()
        visuals.VisualNode.__init__(self, parent=parent, name=self.name)
        self.freeze()
