from typing import NamedTuple


class AxisTuple(NamedTuple):
    """NamedTuple that stores any data that could be bound on axes x and y.

    For example, it could be size (x - width, y - height), points (coordinates
    x and y), etc.
    """

    x: int
    y: int
