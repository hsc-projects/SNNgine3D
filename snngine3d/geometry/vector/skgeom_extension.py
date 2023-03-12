from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
from skgeom import Point2, Point3, Segment2, Segment3, Vector2, Vector3
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


# class Segment:


class Segment2D(Segment2):

    def to_numpy(self):
        return np.array([self.source().to_numpy(),
                         self.target().to_numpy()])

    @classmethod
    def from_numpy(cls, arr0: np.ndarray, arr1: Optional[np.ndarray] = None):

        if arr1 is None:
            if arr0.shape != (2, 2):
                raise AssertionError
            arr1 = arr0[1]
            arr0 = arr0[0]
        return cls(Point2D.from_numpy(arr0),
                   Point2D.from_numpy(arr1))

    @classmethod
    def from_vector(cls, vector: Vector2, source: Optional[Point2D] = None):
        if source is None:
            source = Point2D(0, 0)
        return cls(source, source + vector)


class Segment3D(Segment3):

    def to_numpy(self):
        return np.array([self.source().to_numpy(),
                         self.target().to_numpy()])

    @classmethod
    def from_numpy(cls, arr0: np.ndarray, arr1: Optional[np.ndarray] = None):
        if arr1 is None:
            if arr0.shape != (2, 3):
                raise AssertionError
            arr1 = arr0[1]
            arr0 = arr0[0]
        return cls(Point3D.from_numpy(arr0),
                   Point3D.from_numpy(arr1))


@dataclass(frozen=True)
class Segment1DArray:
    array: np.ndarray = field(default_factory=lambda: np.zeros((2, 1), dtype=np.float))

    def __post_init__(self):
        self.validate()  # validation

    def source(self):
        return self.array[0]

    def set_source(self, value):
        self.array[0][:] = value
        return self

    def target(self):
        return self.array[1]

    def set_target(self, value):
        self.array[1][:] = value
        return self

    def to_vector(self):
        return self.array[1] - self.array[0]

    def set_array(self, value):
        self.array[:] = value
        return self

    def validate(self):
        if self.array.shape != (2, 1):
            raise TypeError


@dataclass(frozen=True)
class Segment2DArray(Segment1DArray):
    array: np.ndarray = field(default_factory=lambda: np.zeros((2, 2), dtype=np.float))

    # noinspection PyPep8Naming
    def as_segment(self):
        return Segment2D.from_numpy(self.array)

    @classmethod
    def from_numpy(cls, arr0: np.ndarray, arr1: Optional[np.ndarray] = None):
        if arr1 is not None:
            arr0 = np.array([arr0, arr1])
        return cls(arr0)

    @classmethod
    def from_vector(cls, vector: Union[Vector2, np.ndarray],
                    source: Optional[Union[Point2D, np.ndarray]] = None):
        if source is None:
            if not isinstance(vector, Vector2):
                source = np.array([0., 0.])
            else:
                source = Point2D(0, 0)

        return cls(array=np.array([source, source + vector]))

    def validate(self):
        self.as_segment()


@dataclass(frozen=True)
class Segment3DArray(Segment2DArray):
    array: np.ndarray = field(default_factory=lambda: np.zeros((2, 3), dtype=np.float))

    # noinspection PyPep8Naming
    def as_segment(self):
        return Segment3D.from_numpy(self.array)

    @classmethod
    def from_vector(cls, vector: Union[Vector3, np.ndarray],
                    source: Optional[Union[Point3D, np.ndarray]] = None):
        if source is None:
            if not isinstance(vector, Vector3):
                source = np.array([0., 0., 0.])
            else:
                source = Point3D(0, 0, 0)
        return cls(array=np.array([source, source + vector]))


@dataclass(frozen=True)
class Segment4DArray(Segment2DArray):
    array: np.ndarray = field(default_factory=lambda: np.array([[0., 0., 1., 1.],
                                                                [0., 0., 1., 1.]],
                                                               dtype=np.float))

    # noinspection PyPep8Naming
    def as_segment(self):
        raise NotImplementedError

    @classmethod
    def from_vector(cls, vector: np.ndarray,
                    source: np.ndarray = None):
        if source is None:
            source = np.array([0., 0., 0., 0.])
        return cls(array=np.array([source, source + vector]))

    # noinspection PyPep8Naming
    def validate(self):
        if self.array.shape != (2, 4):
            raise AttributeError


@dataclass(frozen=True)
class Segment4DArrayCanvas(Segment4DArray):
    segment2d: Segment2DArray = field(default_factory=lambda: Segment2DArray())

    def __post_init__(self):
        super().__post_init__()
        # if self.array[0][3] == 0:
        self.segment2d.set_source(self.array[0][:2] / self.array[0][3])
        # if self.array[1][3] != 0:
        self.segment2d.set_target(self.array[1][:2] / self.array[1][3])

    # noinspection PyPep8Naming
    def as_segment(self):
        raise NotImplementedError

    def set_array(self, value):
        super().set_array(value)
        self.segment2d.set_source(self.array[0][:2] / self.array[0][3])
        self.segment2d.set_target(self.array[1][:2] / self.array[1][3])
        return self

    def set_target(self, value):
        super().set_target(value)
        self.segment2d.set_target(self.array[1][:2] / self.array[1][3])
        return self

    def set_source(self, value):
        super().set_source(value)
        self.segment2d.set_source(self.array[0][:2] / self.array[0][3])
        return self
