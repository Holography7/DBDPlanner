from typing import Self

import pytest
from PIL.Image import Resampling

from src.enums import StrColor
from src.renderer import PlanRenderer
from src.schemas import CustomizationSettings, PathSettings, Settings
from src.types import BoxTuple, CoordinatesTuple, Dimensions, PlanCell, Size
from src.utils import correct_paths


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
    def test_get_cell_box(
        self: Self,
        plan_cell: PlanCell,
        dimensions: Dimensions,
        plan_margins: BoxTuple,
        cell_paddings: BoxTuple,
        cell_size: Size,
    ) -> None:
        """Test getting cell box.

        :param PlanCell plan_cell: fixture of plan cell (cell coordinate with
         row and column).
        :param Dimensions dimensions: fixture of dimensions of plan.
        :param BoxTuple plan_margins: fixture of plan margins.
        :param BoxTuple cell_paddings: fixture of cell paddings.
        :param Size cell_size: fixture of cell size.
        :returns: None
        """
        paths = {
            'header_font': 'fonts/OpenSans-Regular.ttf',
            'body_font': 'fonts/OpenSans-Regular.ttf',
            'placeholders': 'images',
            'plans': 'plans',
        }
        corrected_paths = correct_paths(initial=paths)
        path_settings = PathSettings(**corrected_paths)
        customization_settings = CustomizationSettings(
            header_font_size=1,
            body_font_size=1,
            header_text_color=StrColor.BLACK,
            body_text_color=StrColor.BLACK,
            background_color=StrColor.BLACK,
            plan_margins=plan_margins,
            cell_paddings=cell_paddings,
            cell_size=cell_size,
            resampling_method=Resampling.LANCZOS,
        )
        settings = Settings(
            paths=path_settings,
            customization=customization_settings,
        )
        cell_coordinate_out_of_bounds = (
            plan_cell.row > dimensions.rows
            or plan_cell.column > dimensions.columns
        )
        if cell_coordinate_out_of_bounds:
            expected = None
        else:
            top = (
                plan_margins.top
                + cell_paddings.top
                + (cell_size.height * plan_cell.row)
            )
            left = (
                plan_margins.left
                + cell_paddings.left
                + (cell_size.width * plan_cell.column)
            )
            bottom = top + cell_size.height - cell_paddings.y
            right = left + cell_size.width - cell_paddings.x
            expected = BoxTuple(top=top, right=right, bottom=bottom, left=left)
        renderer = PlanRenderer(dimensions=dimensions, settings=settings)

        if cell_coordinate_out_of_bounds:
            with pytest.raises(ValueError):
                renderer.get_cell_box(cell=plan_cell)
            return
        result = renderer.get_cell_box(cell=plan_cell)

        assert result == expected

    def test_get_font(self: Self) -> None:
        """Test getting font from included global mapping.

        :returns: None
        """
        pytest.skip(reason='Not implemented')
