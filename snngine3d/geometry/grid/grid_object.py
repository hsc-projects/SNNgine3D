import numpy as np


class GridDirectionsObject:

    directions = {
        '+x': 0,
        '-x': 1,
        '+y': 2,
        '-y': 3,
        '+z': 4,
        '-z': 5,
    }

    coord = np.array([
        [-1, 0, 0],
        [1, 0, 0],
        [0, 1, 0],
        [0, -1, 0],
        [0, 0, -1],
        [0, 0, 1],
    ])

    def __init__(self, obj):
        self._index = 0
        self._obj = obj

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._obj[item]
        elif isinstance(item, str):
            return self._obj[self.directions[item]]

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index > 5:
            raise StopIteration
        next_ = self[self._index]
        self._index += 1
        return next_
