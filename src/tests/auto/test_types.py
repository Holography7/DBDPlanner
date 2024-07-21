from collections.abc import Sequence
from typing import Self

import pytest

from src.types import BoxTuple, Size


class TestBoxTuple:
    """Testing BoxTuple."""

    @pytest.mark.parametrize('size', (0, 1, 5, 10, 15))
    def test_create_square(self: Self, size: int) -> None:
        """Testing creating BoxTuple as square.

        :param int size: square size.
        :returns: None
        """
        expected = BoxTuple(top=size, right=size, bottom=size, left=size)

        actual = BoxTuple.create_square(size=size)

        assert actual == expected

    @pytest.mark.parametrize(
        ('sequence', 'expected'),
        (
            ((0,), BoxTuple(top=0, right=0, bottom=0, left=0)),
            ((1, 5), BoxTuple(top=1, right=5, bottom=1, left=5)),
            ((10, 15, 1), BoxTuple(top=10, right=15, bottom=1, left=15)),
            ((5, 10, 15, 0), BoxTuple(top=5, right=10, bottom=15, left=0)),
        ),
        ids=tuple(f'{count} element' for count in range(1, 5)),
    )
    def test_from_sequence(
        self: Self,
        sequence: Sequence[int],
        expected: BoxTuple,
    ) -> None:
        """Testing creating BoxTuple from sequence with 1-4 elements.

        :param Sequence[int] sequence: sequence with 1-4 elements.
        :param BoxTuple expected: expected BoxTuple.
        :returns: None
        """
        actual = BoxTuple.from_sequence(sequence=sequence)

        assert actual == expected

    @pytest.mark.parametrize(
        ('value', 'expected'),
        (
            (35, BoxTuple(top=35, right=35, bottom=35, left=35)),
            ((4,), BoxTuple(top=4, right=4, bottom=4, left=4)),
            ((7, 3), BoxTuple(top=7, right=3, bottom=7, left=3)),
            ((6, 2, 1), BoxTuple(top=6, right=2, bottom=1, left=2)),
            ((9, 10, 8, 0), BoxTuple(top=9, right=10, bottom=8, left=0)),
        ),
        ids=('Integer', *(f'{count} element' for count in range(1, 5))),
    )
    def test_from_int_or_sequence(
        self: Self,
        value: int | Sequence[int],
        expected: BoxTuple,
    ) -> None:
        """Testing creating BoxTuple from sequence with 1-4 elements or int.

        :param int | Sequence[int] value: sequence or int with 1-4 elements.
        :param BoxTuple expected: expected BoxTuple.
        :returns: None
        """
        actual = BoxTuple.from_int_or_sequence(value=value)

        assert actual == expected

    def test_x(self: Self, box_tuple: BoxTuple) -> None:
        """Testing getting sum of x-axis values (left and right).

        :param BoxTuple box_tuple: fixture of BoxTuple.
        :returns: None
        """
        expected = box_tuple.left + box_tuple.right

        actual = box_tuple.x

        assert actual == expected

    def test_y(self: Self, box_tuple: BoxTuple) -> None:
        """Testing getting sum of y-axis values (top and bottom).

        :param BoxTuple box_tuple: fixture of BoxTuple.
        :returns: None
        """
        expected = box_tuple.top + box_tuple.bottom

        actual = box_tuple.y

        assert actual == expected

    def test_size(self: Self, box_tuple: BoxTuple) -> None:
        """Testing getting size of box.

        :param BoxTuple box_tuple: fixture of BoxTuple.
        :returns: None
        """
        expected = Size(
            width=box_tuple.right - box_tuple.left,
            height=box_tuple.bottom - box_tuple.top,
        )

        actual = box_tuple.size

        assert actual == expected
