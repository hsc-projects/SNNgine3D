from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Optional, Union

from vispy.visuals.transforms import STTransform

from snngine3d.vispy_torch_interop.rendered_objects.rendered_object import RenderedObjectNode
from snngine3d.vispy_torch_interop.utils import XYZObject


@dataclass
class _STR:

    parent: RenderedObjectNode
    # grid: NetworkGrid
    prop_id: str = 'some key'

    spin_box_sliders: Optional[XYZObject] = None

    value_ranges: Optional[XYZObject] = None

    _min_value: Optional[Union[int, float]] = None
    _max_value: Optional[Union[int, float]] = None

    def __call__(self):
        return getattr(self.parent.transform, self.prop_id)

    # noinspection PyArgumentList
    def __post_init__(self):
        if self.spin_box_sliders is None:
            self.spin_box_sliders = XYZObject()

        if (self._min_value is not None) or (self._max_value is not None):
            if self.value_ranges is not None:
                raise ValueError('multiple values for self.value_intervals.')
            self.value_ranges = XYZObject(
                x=pd.Interval(self._min_value, self._max_value, closed='both'),
                y=pd.Interval(self._min_value, self._max_value, closed='both'),
                z=pd.Interval(self._min_value, self._max_value, closed='both'))

    def change_prop(self, i, v):
        if self.value_ranges is not None:
            interval = self.value_ranges[i]
            v = min(interval.right, max(interval.left, v))
        p = getattr(self.transform, self.prop_id)
        p[i] = v
        setattr(self.transform, self.prop_id, p)
        if self.parent.transform_connected is True:
            self.parent.transform_changed()

    @property
    def transform(self) -> STTransform:
        return self.parent.transform

    @property
    def x(self):
        return getattr(self.transform, self.prop_id)[0]

    @x.setter
    def x(self, v):
        self.change_prop(0, v)

    @property
    def y(self):
        return getattr(self.transform, self.prop_id)[1]

    @y.setter
    def y(self, v):
        self.change_prop(1, v)

    @property
    def z(self):
        return getattr(self.transform, self.prop_id)[2]

    @z.setter
    def z(self, v):
        self.change_prop(2, v)

    @property
    def a(self):
        return getattr(self.transform, self.prop_id)[3]

    @a.setter
    def a(self, v):
        self.change_prop(3, v)


@dataclass
class Scale(_STR):
    prop_id: str = 'scale'

    min_value: Optional[int] = 0
    max_value: Optional[int] = 10


@dataclass
class Translate(_STR):
    _grid_unit_shape: Optional[tuple] = None
    prop_id: str = 'translate'

    min_value: Optional[int] = -5
    max_value: Optional[int] = 5

    def __post_init__(self):
        super().__post_init__()
        self._grid_coordinates = np.zeros(3)

    def _move(self, i):
        self.transform.move(self.parent.grid.movements[i])
        self._grid_coordinates += self.parent.grid.movements.coord[i]

        if self.parent.transform_connected is True:
            self.parent.transform_changed()

        self.spin_box_sliders[int(i/2)].actualize_values()

    def mv_left(self):
        self._move(0)

    def mv_right(self):
        self._move(1)

    def mv_fw(self):
        self._move(2)

    def mv_bw(self):
        self._move(3)

    def mv_up(self):
        self._move(4)

    def mv_down(self):
        self._move(5)
