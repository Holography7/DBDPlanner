from typing import Self

import pytest

from src.enums import StrColor
from src.renderer import PlanRenderer
from src.schemas import CustomizationSettings
from src.types import BoxTuple, CoordinatesTuple, Dimensions, Size


class TestPlanRenderer:
    """Test cases for class that rendering plan image."""

    def test_get_coordinates_where_draw_text(
        self: Self,
        box_tuple: BoxTuple,
        object_size: Size,
    ) -> None:
        """Testing getting coordinates for drawing text in box.

        :param BoxTuple box_tuple: fixture of box coordinates inside which need
         draw text.
        :param Size object_size: fixture of size of object.
        :returns: None
        """
        box_size = box_tuple.size
        object_bigger_than_box = (
            box_size.width < object_size.width
            or box_size.height < object_size.height
        )
        if object_bigger_than_box:
            expected = None
        else:
            expected = CoordinatesTuple(
                x=box_tuple.left + (box_size.width - object_size.width) // 2,
                y=box_tuple.top + (box_size.height - object_size.height) // 2,
            )

        if object_bigger_than_box:
            with pytest.raises(ValueError):
                PlanRenderer.get_coordinate_to_place_object_at_center(
                    box=box_tuple,
                    object_size=object_size,
                )
            return
        result = PlanRenderer.get_coordinate_to_place_object_at_center(
            box=box_tuple,
            object_size=object_size,
        )

        assert result == expected

    # Complicated test, but necessary
    def test_get_cell_box(  # noqa: PLR0913
        self: Self,
        row: int,
        column: int,
        dimensions: Dimensions,
        plan_margins: BoxTuple,
        cell_paddings: BoxTuple,
        cell_size: Size,
    ) -> None:
        """Test getting cell box.

        :param int row: fixture of row index.
        :param int column: fixture of column index.
        :param Dimensions dimensions: fixture of dimensions of plan.
        :param BoxTuple plan_margins: fixture of plan margins.
        :param BoxTuple cell_paddings: fixture of cell paddings.
        :param Size cell_size: fixture of cell size.
        :returns: None
        """
        settings = CustomizationSettings(
            header_font_size=1,
            body_font_size=1,
            header_text_color=StrColor.BLACK,
            body_text_color=StrColor.BLACK,
            background_color=StrColor.BLACK,
            plan_margins=plan_margins,
            cell_paddings=cell_paddings,
            cell_size=cell_size,
        )
        cell_coordinate_out_of_bounds = (
            row > dimensions.rows or column > dimensions.columns
        )
        if cell_coordinate_out_of_bounds:
            expected = None
        else:
            top = plan_margins.top + cell_paddings.top + cell_size.height * row
            left = (
                plan_margins.left
                + cell_paddings.left
                + (cell_size.width * column)
            )
            bottom = top + cell_size.height - cell_paddings.y
            right = left + cell_size.width - cell_paddings.x
            expected = BoxTuple(top=top, right=right, bottom=bottom, left=left)
        renderer = PlanRenderer(dimensions=dimensions, settings=settings)

        if cell_coordinate_out_of_bounds:
            with pytest.raises(ValueError):
                renderer.get_cell_box(row=row, column=column)
            return
        result = renderer.get_cell_box(row=row, column=column)

        assert result == expected
