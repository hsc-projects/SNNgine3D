from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
from typing import Optional, Union

from .skgeom_extension import Point2D, Segment2D, Segment2DArray


@dataclass(frozen=True)
class CursorDragResult2D(Segment2DArray):

    factor: np.ndarray = field(default_factory=lambda: np.array([0.]))

    @classmethod
    def from_drag(cls, dragged_seg: Union[Segment2DArray, Segment2D],
                  drag_seg: Union[Segment2DArray, Segment2D]
                  ) -> CursorDragResult2D:
        return_obj: CursorDragResult2D = cls()
        return return_obj.update(dragged_seg=dragged_seg, drag_seg=drag_seg)

    def update(self, dragged_seg: Union[Segment2DArray, Segment2D],
               drag_seg: Union[Segment2DArray, Segment2D]
               ) -> CursorDragResult2D:
        src = dragged_seg.source()
        trgt = dragged_seg.target()
        self.set_source(trgt)
        vec = dragged_seg.to_vector()
        drag_dim = np.argmax(vec)
        drag_diff = (drag_seg.target()[drag_dim]
                     - drag_seg.source()[drag_dim])
        if (drag_diff == 0) or (src[drag_dim] == trgt[drag_dim]):
            self.factor[0] = 1
            self.set_target(dragged_seg.target())
        else:
            drag_dim_length_self = trgt[drag_dim] - src[drag_dim]
            self.factor[0] = ((drag_dim_length_self + drag_diff) / drag_dim_length_self)
            self.set_target(src + vec * self.factor)
        return self

# @dataclass(frozen=True)
# class CustomLineSegment:
#
#     @dataclass
#     class DragResult:
#         seg: Optional[CustomLineSegment] = None
#         factor: int = 0
#
#         def __post_init__(self):
#             if self.valid is False:
#                 raise AttributeError
#
#         @property
#         def initialized(self) -> bool:
#             return not ((self.seg is None)
#                         and (self.factor == 0))
#
#         @property
#         def invert_drag(self):
#             return self.seg.p_start + self.seg.vec / self.factor
#
#         @property
#         def valid(self) -> bool:
#             if self.initialized is False:
#                 return True
#             return not ((self.seg is None)
#                         or (self.factor == 0))
#
#     p_start: np.ndarray
#     p_end: np.ndarray
#
#     _last_drag_result = DragResult()
#
#     def __post_init__(self):
#
#         if self._last_drag_result.initialized is True:
#             raise AttributeError(
#                 f"({self.__class__.__name__}) "
#                 f"Internal DragResult was initialized")
#         self._last_drag_result.factor = 1
#
#         if self.p_start.shape != self.p_end.shape:
#             raise AttributeError(
#                 f"({self.__class__.__name__}) "
#                 f"self.p_start.shape = {self.p_start.shape} "
#                 f"!= {self.p_end.shape} = self.p_end.shape")
#
#         cond_ndim_start = self.p_start.ndim != 1
#         if cond_ndim_start or (self.p_end.ndim != 1):
#             if cond_ndim_start:
#                 raise AttributeError(
#                     f"({self.__class__.__name__}) "
#                     f"self.p_start.ndim = {self.p_start.ndim} != 1")
#             else:
#                 raise AttributeError(
#                     f"({self.__class__.__name__}) "
#                     f"self.p_end.ndim = {self.p_end.ndim} != 1")
#
#     @property
#     def array(self):
#         return np.array([self.p_start, self.p_end])
#
#     @array.setter
#     def array(self, arr):
#         self.set_points(arr)
#
#     @property
#     def dirs(self):
#         return np.where(self.vec >= 0, 1, -1)
#
#     @classmethod
#     def from_array(cls, arr):
#         if arr.shape[0] != 2:
#             raise ValueError
#         return cls(p_start=arr[0], p_end=arr[1])
#
#     @property
#     def length(self):
#         return np.linalg.norm(self.vec)
#
#     @property
#     def ndim(self):
#         return len(self.p_start)
#
#     def set_p_start(self, arr):
#         if arr.shape != self.p_start.shape:
#             raise ValueError
#         self.p_start[:] = arr
#
#     def set_p_end(self, arr):
#         if arr.shape != self.p_end.shape:
#             raise ValueError
#         self.p_end[:] = arr
#
#     def set_points(self, arr):
#         if arr.shape[0] != 2:
#             raise ValueError
#         self.set_p_start(arr[0])
#         self.set_p_start(arr[1])
#
#     @property
#     def vec(self):
#         return self.p_end - self.p_start
#
#     def drag_from_cursor(self, drag_line_seg: CustomLineSegment,
#                          ) -> DragResult:
#         if self.ndim == 2:
#             vec = self.vec
#             drag_dim = np.argmax(vec)[0]
#
#             flat_drag_p_start = drag_line_seg.p_start[drag_dim]
#             flat_drag_p_end = drag_line_seg.p_end[drag_dim]
#
#             if ((self.p_start[drag_dim] == self.p_end[drag_dim])
#                or (flat_drag_p_start == flat_drag_p_end)):
#                 self._last_drag_result.factor = 1
#                 return self._last_drag_result
#
#             drag_dim_length_self = self.p_end[drag_dim] - self.p_start[drag_dim]
#             self._last_drag_result.factor = \
#                 ((drag_dim_length_self + (flat_drag_p_end - flat_drag_p_start))
#                  / drag_dim_length_self)
#             self.set_p_end(self.p_start + vec * self._last_drag_result.factor)
#             return self._last_drag_result
#         else:
#             raise NotImplementedError


if __name__ == '__main__':
    pass
