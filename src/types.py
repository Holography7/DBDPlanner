from typing import NamedTuple


class CoordinatesTuple(NamedTuple):
    """NamedTuple that stores coordinates on axes x and y."""

    x: int
    y: int


class BoxTuple(NamedTuple):
    """NamedTuple that stores any data bound with box sides.

    For example, it could be coordinates of 2 angles of box: left+top and
    right+bottom. Also, it could be dimensions of margins or paddings from
    left, top, right and bottom sides of box.
    """

    top: int
    right: int
    bottom: int
    left: int


class Dimensions(NamedTuple):
    """NamedTuple that stores width and height."""

    width: int
    height: int


class RGBColor(NamedTuple):
    """NamedTuple that stores values of RGB colors."""

    red: int
    green: int
    blue: int
