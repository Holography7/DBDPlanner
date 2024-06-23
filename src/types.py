from pathlib import Path
from typing import NamedTuple, Self, TypedDict


class CoordinatesTuple(NamedTuple):
    """NamedTuple that stores coordinates on axes x and y."""

    x: int
    y: int

    def __repr__(self: Self) -> str:
        """Representation CoordinatesTuple like 10x10.

        :returns: string like 10x10.
        """
        return f'{self.x}x{self.y}'


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

    @property
    def x(self: Self) -> int:
        """Get sum of coordinates from left and right.

        :returns: sum of coordinates from left and right.
        """
        return self.left + self.right

    @property
    def y(self: Self) -> int:
        """Get sum of coordinates from top and bottom.

        :returns: sum of coordinates from top and bottom.
        """
        return self.top + self.bottom


class Size(NamedTuple):
    """NamedTuple that stores width and height."""

    width: int
    height: int


class RGBColor(NamedTuple):
    """NamedTuple that stores values of RGB colors."""

    red: int
    green: int
    blue: int


class Dimensions(NamedTuple):
    """NamedTuple that stores rows and columns."""

    rows: int
    columns: int


class FontParams(TypedDict):
    """TypedDict of params for loading fonts."""

    font: Path
    size: int
