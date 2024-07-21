from collections.abc import Sequence
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

    @classmethod
    def create_square(cls: type[Self], size: NonNegativeInt) -> Self:
        """Create instance as square (box with sides with same size).

        :param NonNegativeInt size: size of all sides of box.
        :returns: BoxTuple with same size of sides.
        """
        if size < 0:
            msg = 'Value must be positive integer'
            raise ValueError(msg)
        return cls(top=size, right=size, bottom=size, left=size)

    @classmethod
    def from_sequence(
        cls: type[Self],
        sequence: Sequence[NonNegativeInt],
    ) -> Self:
        """Create instance from sequence with 1-4 elements.

        It will place values like it do HTML:
        1 element - all sides (square).
        2 elements - first for top and bottom, second for left and right.
        3 elements - first for top, second for left and right, third for
         bottom.
        4 elements - top, right, bottom and left respectively.
        :param Sequence[NonNegativeInt] sequence: sequence that will convert to
         box. Must be with 1-4 elements.
        :returns: BoxTuple with same size of sides.
        """
        match len(sequence):
            case 1:
                return cls.create_square(size=sequence[0])
            case 2:
                return cls(
                    top=sequence[0],
                    right=sequence[1],
                    bottom=sequence[0],
                    left=sequence[1],
                )
            case 3:
                return cls(
                    top=sequence[0],
                    right=sequence[1],
                    bottom=sequence[2],
                    left=sequence[1],
                )
            case 4:
                return cls(*sequence)
            case _:
                msg = 'Value must be with 1-4 elements.'
                raise ValueError(msg)

    @classmethod
    def from_int_or_sequence(
        cls: type[Self],
        value: NonNegativeInt | Sequence[NonNegativeInt],
    ) -> Self:
        """Create instance from integer or sequence with 1-4 elements.

        If got integer or sequence with 1 element, returns box as square.
        If got sequence with 2-4 elements, it will place values like in HTML:
        2 elements - first for top and bottom, second for left and right.
        3 elements - first for top, second for left and right, third for
         bottom.
        4 elements - top, right, bottom and left respectively.
        :param NonNegativeInt | Sequence[NonNegativeInt] value: integer or
        sequence that will convert to box. Must be with 1-4 elements.
        :returns: BoxTuple with same size of sides.
        """
        if type(value) not in {int, list, tuple}:
            msg = 'Value must be integer or list/tuple with 1-4 elements'
            raise ValueError(msg)
        if isinstance(value, int):
            return cls.create_square(size=value)
        return cls.from_sequence(sequence=value)

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
