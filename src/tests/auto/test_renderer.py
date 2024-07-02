from typing import Self

import pytest

from src.renderer import PlanRenderer
from src.types import BoxTuple, CoordinatesTuple, Size


class TestPlanRenderer:
    """Test cases for class that rendering plan image."""

    CASES_FOR_PLACE_OBJECT = (
        # Scheme:
        # 1. Box inside which need to place object
        # 2. Object size
        # 3. Expected coordinate where need to place object
        (
            BoxTuple(top=10, right=20, bottom=20, left=10),
            Size(width=10, height=10),
            CoordinatesTuple(x=10, y=10),
        ),
        (
            BoxTuple(top=0, right=10, bottom=10, left=0),
            Size(width=10, height=10),
            CoordinatesTuple(x=0, y=0),
        ),
        (
            BoxTuple(top=10, right=100, bottom=100, left=10),
            Size(width=50, height=50),
            CoordinatesTuple(x=30, y=30),
        ),
        (
            BoxTuple(top=5, right=100, bottom=65, left=10),
            Size(width=70, height=30),
            CoordinatesTuple(x=20, y=20),
        ),
    )
    CASES_FOR_PLACE_OBJECT_FAIL = (
        # Scheme:
        # 1. Box inside which need place object
        # 2. Object size. For that test, it must be larger than box.
        (
            BoxTuple(top=0, right=10, bottom=10, left=0),
            Size(width=11, height=11),
        ),
        (
            BoxTuple(top=0, right=10, bottom=10, left=0),
            Size(width=11, height=10),
        ),
        (
            BoxTuple(top=0, right=10, bottom=10, left=0),
            Size(width=10, height=11),
        ),
    )

    @pytest.mark.parametrize(
        ('box', 'object_size', 'expected_coordinate'),
        CASES_FOR_PLACE_OBJECT,
        ids=(
            f'{case[0]}, object {case[1]}, expected {case[2]}'
            for case in CASES_FOR_PLACE_OBJECT
        ),
    )
    def test_get_coordinates_where_draw_text(
        self: Self,
        box: BoxTuple,
        object_size: Size,
        expected_coordinate: CoordinatesTuple,
    ) -> None:
        """Testing getting coordinates for drawing text in box.

        :param BoxTuple box: parameter with box coordinates inside which need
         draw text.
        :param Size object_size: parameter with size of object.
        :param CoordinatesTuple expected_coordinate: parameter with expected
         coordinates where must draw text.
        :returns: None
        """
        result = PlanRenderer.get_coordinate_to_place_object_at_center(
            box=box,
            object_size=object_size,
        )

        assert result == expected_coordinate

    @pytest.mark.parametrize(
        ('box', 'object_size'),
        CASES_FOR_PLACE_OBJECT_FAIL,
        ids=(
            'Object larger with both dimensions',
            'Object larger with width',
            'Object larger with height',
        ),
    )
    def test_get_coordinates_where_draw_text_fail(
        self: Self,
        box: BoxTuple,
        object_size: Size,
    ) -> None:
        """Testing getting coordinates for drawing text in box: failing cases.

        :param BoxTuple box: parameter with box coordinates inside which need
         to draw text.
        :param Size object_size: parameter with size of object. For that
         test, it must be larger than box.
        :returns: None
        """
        with pytest.raises(ValueError):
            PlanRenderer.get_coordinate_to_place_object_at_center(
                box=box,
                object_size=object_size,
            )
