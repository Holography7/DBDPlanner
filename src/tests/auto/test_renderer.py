from typing import Self

import pytest

from src.renderer import PlanRenderer
from src.types import AxisTuple


class TestPlanRenderer:
    """Test cases for class that rendering plan image."""

    CASES_FOR_TEXT_DRAWING = (
        (
            AxisTuple(x=10, y=10),  # left top coordinate of box
            AxisTuple(x=10, y=10),  # box size
            AxisTuple(x=10, y=10),  # textbox size
            AxisTuple(x=10, y=10),  # expected coordinate where draw text
        ),
        (
            AxisTuple(x=0, y=0),  # left top coordinate of box
            AxisTuple(x=10, y=10),  # box size
            AxisTuple(x=10, y=10),  # textbox size
            AxisTuple(x=0, y=0),  # expected coordinate where draw text
        ),
        (
            AxisTuple(x=10, y=10),  # left top coordinate of box
            AxisTuple(x=90, y=90),  # box size
            AxisTuple(x=50, y=50),  # textbox size
            AxisTuple(x=30, y=30),  # expected coordinate where draw text
        ),
        (
            AxisTuple(x=10, y=5),  # left top coordinate of box
            AxisTuple(x=90, y=60),  # box size
            AxisTuple(x=70, y=30),  # textbox size
            AxisTuple(x=20, y=20),  # expected coordinate where draw text
        ),
    )
    CASES_FOR_PASTING_PLACEHOLDER = (
        (
            AxisTuple(x=7, y=5),  # plan dimensions
            AxisTuple(x=300, y=300),  # cell size
            2,  # element number
            AxisTuple(x=10, y=10),  # expected coordinates
        ),
    )

    @pytest.mark.parametrize(
        ('left_top', 'box_size', 'textbox_size', 'expected_coordinate'),
        CASES_FOR_TEXT_DRAWING,
        ids=(
            (
                f'Box coordinate = {case[0]}, box size = {case[1]}, textbox '
                f'size = {case[2]}, expected coordinate = {case[3]}'
            )
            for case in CASES_FOR_TEXT_DRAWING
        ),
    )
    def test_get_coordinates_where_draw_text(
        self: Self,
        left_top: AxisTuple,
        box_size: AxisTuple,
        textbox_size: AxisTuple,
        expected_coordinate: AxisTuple,
    ) -> None:
        """Testing getting coordinates for drawing text in box.

        :param AxisTuple left_top: parameter with left-top coordinate of box
         where need to draw text.
        :param AxisTuple box_size: parameter with size of box where need to
         draw text.
        :param AxisTuple textbox_size: parameter with size of textbox where
         need to draw text.
        :param AxisTuple expected_coordinate: parameter with expected
         coordinates where must draw text.
        :returns: None
        """
        result = PlanRenderer.get_coordinates_where_draw_text(
            left_top=left_top,
            box_size=box_size,
            textbox_size=textbox_size,
        )

        assert result == expected_coordinate

    @pytest.mark.parametrize(
        ('box_size', 'textbox_size'),
        (
            (AxisTuple(x=10, y=10), AxisTuple(x=11, y=11)),
            (AxisTuple(x=10, y=10), AxisTuple(x=11, y=10)),
            (AxisTuple(x=10, y=10), AxisTuple(x=10, y=11)),
        ),
        ids=(
            'Textbox larger with both dimensions',
            'Textbox larger with width',
            'Textbox larger with height',
        ),
    )
    def test_get_coordinates_where_draw_text_fail(
        self: Self,
        box_size: AxisTuple,
        textbox_size: AxisTuple,
    ) -> None:
        """Testing getting coordinates for drawing text in box: failing cases.

        :param AxisTuple box_size: parameter with size of box where need to
         draw text.
        :param AxisTuple textbox_size: parameter with size of textbox where
         need to draw text. For that test, it must be larger than box_size.
        :returns: None
        """
        left_top = AxisTuple(x=0, y=0)

        with pytest.raises(ValueError):
            PlanRenderer.get_coordinates_where_draw_text(
                left_top=left_top,
                box_size=box_size,
                textbox_size=textbox_size,
            )

    @pytest.mark.parametrize(
        (
            'dimensions',
            'cell_size',
            'element_num',
            'expected_coordinate',
        ),
        CASES_FOR_PASTING_PLACEHOLDER,
    )
    def test_get_coordinate_to_paste_placeholder(self: Self) -> None:
        """Testing getting coordinate to place placeholder."""
