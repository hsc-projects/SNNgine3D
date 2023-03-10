from __future__ import annotations

import numpy as np
from skgeom import Point2, Point3, Segment2, Segment3
from typing import Optional, Union


class Point2D(Point2):

    def __getitem__(self, item):
        if item == 0:
            return self.x()
        elif item == 1:
            return self.y()
        else:
            raise IndexError

    @classmethod
    def from_numpy(cls, arr: np.ndarray) -> Point2D:
        if arr.shape != (2,):
            raise TypeError
        return cls(arr[0], arr[1])

    def to_numpy(self):
        return np.array([self.x(), self.y()])


class Point3D(Point3):

    def __getitem__(self, item):
        if item == 0:
            return self.x()
        elif item == 1:
            return self.y()
        elif item == 2:
            return self.z()
        else:
            raise IndexError

    @classmethod
    def from_numpy(cls, arr: np.ndarray) -> Point3D:
        if arr.shape != (3,):
            raise TypeError
        return cls(arr[0], arr[1], arr[2])

    def to_numpy(self):
        return np.array([self.x(), self.y(), self.z()])


class Segment:

    def to_numpy(self: Union[Segment, Segment2D]):
        return np.array([self.source().to_numpy(),
                         self.target().to_numpy()])


class Segment2D(Segment2, Segment):

    @classmethod
    def from_numpy(cls, arr0: np.ndarray, arr1: Optional[np.ndarray] = None):
        if arr1 is None:
            if arr0.shape != (2, 2):
                raise AssertionError
            arr1 = arr0[1]
            arr0 = arr0[0]
        return cls(Point2D.from_numpy(arr0),
                   Point2D.from_numpy(arr1))


class Segment3D(Segment3, Segment):

    @classmethod
    def from_numpy(cls, arr0: np.ndarray, arr1: Optional[np.ndarray] = None):
        if arr1 is None:
            if arr0.shape != (2, 3):
                raise AssertionError
            arr1 = arr0[1]
            arr0 = arr0[0]
        return cls(Point3D.from_numpy(arr0),
                   Point3D.from_numpy(arr1))
