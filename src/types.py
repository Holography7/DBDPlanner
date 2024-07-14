from pathlib import Path
from typing import NamedTuple, Self, TypedDict

from pydantic import NonNegativeInt


class CoordinatesTuple(NamedTuple):
    """NamedTuple that stores coordinates on axes x and y."""

    x: int
    y: int

    def __repr__(self: Self) -> str:
        """Representation like Coordinate 10x10.

        :returns: string like Coordinate 10x10.
        """
        return f'Coordinate {self.x}x{self.y}'


class Size(NamedTuple):
    """NamedTuple that stores width and height."""

    width: NonNegativeInt
    height: NonNegativeInt

    def __repr__(self: Self) -> str:
        """Representation like "Size 10x10".

        :returns: string like "Size 10x10".
        """
        return f'Size {self.width}x{self.height}'


class BoxTuple(NamedTuple):
    """NamedTuple that stores any data bound with box sides.

    For example, it could be coordinates of 2 angles of box: left+top and
    right+bottom. Also, it could be dimensions of margins or paddings from
    left, top, right and bottom sides of box.
    """

    top: NonNegativeInt
    right: NonNegativeInt
    bottom: NonNegativeInt
    left: NonNegativeInt

    @property
    def x(self: Self) -> NonNegativeInt:
        """Get sum of coordinates from left and right.

        :returns: sum of coordinates from left and right.
        """
        return self.left + self.right

    @property
    def y(self: Self) -> NonNegativeInt:
        """Get sum of coordinates from top and bottom.

        :returns: sum of coordinates from top and bottom.
        """
        return self.top + self.bottom

    @property
    def size(self: Self) -> Size:
        """Get size of box.

        :returns: Size object.
        """
        return Size(
            width=self.right - self.left,
            height=self.bottom - self.top,
        )

    def __repr__(self: Self) -> str:
        """Representation like "Box (top,left)x(right,bottom)".

        For exemple, box with parameters left=10, top=10, right=20 and
         bottom=20 will represent as (10,10)x(20,20)
        :returns: string like "Box (top,left)x(right,bottom)".
        """
        return f'Box ({self.left},{self.top})x({self.right},{self.bottom})'


class RGBColor(NamedTuple):
    """NamedTuple that stores values of RGB colors."""

    red: NonNegativeInt
    green: NonNegativeInt
    blue: NonNegativeInt


class Dimensions(NamedTuple):
    """NamedTuple that stores rows and columns."""

    rows: NonNegativeInt
    columns: NonNegativeInt

    def __repr__(self: Self) -> str:
        """Representation like "Dimensions (rows = 10, columns = 10)".

        :returns: string like "Dimensions (rows = 10, columns = 10)".
        """
        return f'Dimensions (rows = {self.rows}, columns = {self.columns})'


class PlanCell(NamedTuple):
    """NamedTuple that stores coordinate of cell in plan."""

    row: NonNegativeInt
    column: NonNegativeInt


class FontParams(TypedDict):
    """TypedDict of params for loading fonts."""

    font: Path
    size: NonNegativeInt
