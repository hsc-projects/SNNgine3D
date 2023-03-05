from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class LineSegment:

    p_start: np.ndarray
    p_end: np.ndarray

    def __post_init__(self):

        if self.p_start.shape != self.p_end.shape:
            raise AttributeError

        if (self.p_start.ndim != 1) or (self.p_end.ndim != 1):
            raise AttributeError

    @property
    def array(self):
        return np.array([self.p_start, self.p_end])

    @array.setter
    def array(self, arr):
        self.set_points(arr)

    @property
    def dirs(self):
        return np.where(self.vec >= 0, 1, -1)

    @classmethod
    def from_array(cls, arr):
        if arr.shape[0] != 2:
            raise ValueError
        return cls(p_start=arr[0], p_end=arr[1])

    @property
    def length(self):
        return np.linalg.norm(self.vec)

    def set_p_start(self, arr):
        if arr.shape != self.p_start.shape:
            raise ValueError
        self.p_start[:] = arr

    def set_p_end(self, arr):
        if arr.shape != self.p_end.shape:
            raise ValueError
        self.p_end[:] = arr

    def set_points(self, arr):
        if arr.shape[0] != 2:
            raise ValueError
        self.set_p_start(arr[0])
        self.set_p_start(arr[1])

    @property
    def vec(self):
        return self.p_end - self.p_start

