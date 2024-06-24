from typing import Self

import pytest

from src.renderer import PlanRenderer
from src.types import BoxTuple, CoordinatesTuple, Size


class TestPlanRenderer:
    """Test cases for class that rendering plan image."""

    CASES_FOR_TEXT_DRAWING = (
        # Scheme:
        # 1. Box inside which need draw text
        # 2. Textbox size
        # 3. Expected coordinate where need to draw text
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
    CASES_FOR_TEXT_DRAWING_FAIL = (
        # Scheme:
        # 1. Box inside which need draw text
        # 2. Textbox size. For that test, it must be larger than box.
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
        ('box', 'textbox_size', 'expected_coordinate'),
        CASES_FOR_TEXT_DRAWING,
        ids=(
            f'{case[0]}, textbox {case[1]}, expected {case[2]}'
            for case in CASES_FOR_TEXT_DRAWING
        ),
    )
    def test_get_coordinates_where_draw_text(
        self: Self,
        box: BoxTuple,
        textbox_size: Size,
        expected_coordinate: CoordinatesTuple,
    ) -> None:
        """Testing getting coordinates for drawing text in box.

        :param BoxTuple box: parameter with box coordinates inside which need
         draw text.
        :param Size textbox_size: parameter with size of textbox.
        :param CoordinatesTuple expected_coordinate: parameter with expected
         coordinates where must draw text.
        :returns: None
        """
        result = PlanRenderer.get_coordinates_where_draw_text(
            box=box,
            textbox_size=textbox_size,
        )

        assert result == expected_coordinate

    @pytest.mark.parametrize(
        ('box', 'textbox_size'),
        CASES_FOR_TEXT_DRAWING_FAIL,
        ids=(
            'Textbox larger with both dimensions',
            'Textbox larger with width',
            'Textbox larger with height',
        ),
    )
    def test_get_coordinates_where_draw_text_fail(
        self: Self,
        box: BoxTuple,
        textbox_size: Size,
    ) -> None:
        """Testing getting coordinates for drawing text in box: failing cases.

        :param BoxTuple box: parameter with box coordinates inside which need
         to draw text.
        :param Size textbox_size: parameter with size of textbox. For that
         test, it must be larger than box_size.
        :returns: None
        """
        with pytest.raises(ValueError):
            PlanRenderer.get_coordinates_where_draw_text(
                box=box,
                textbox_size=textbox_size,
            )
