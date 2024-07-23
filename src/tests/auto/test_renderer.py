from typing import Self

import pytest
from PIL import ImageFont
from PIL.Image import Resampling

from src.dataclasses import FontParams
from src.enums import StrColor
from src.global_mappings import FontMapping
from src.renderer import PlanRenderer
from src.schemas import CustomizationSettings
from src.settings import SETTINGS
from src.types import BoxTuple, CoordinatesTuple, Dimensions, PlanCell, Size


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
        settings = SETTINGS.model_copy(
            update={'customization': customization_settings},
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

    def test_get_font_default(self: Self, font_size: int) -> None:
        """Test getting default font renderer.

        :param int font_size: fixture of font size.
        :returns: None
        """
        customization_settings = SETTINGS.customization.model_copy(
            update={'header_font_size': font_size},
        )
        settings = SETTINGS.model_copy(
            update={'customization': customization_settings},
        )
        font_mapping = FontMapping()
        expected = font_mapping.load(
            path=settings.paths.header_font,
            size=font_size,
        )
        renderer = PlanRenderer(
            dimensions=Dimensions(rows=1, columns=1),
            settings=settings,
        )

        actual = renderer.get_font()

        assert actual == expected
        font_mapping.clear()

    def test_get_font_by_params(self: Self, font_size: int) -> None:
        """Test getting font by parameters.

        :param int font_size: fixture of font size.
        :returns: None
        """
        customization_settings = SETTINGS.customization.model_copy(
            update={'header_font_size': font_size},
        )
        settings = SETTINGS.model_copy(
            update={'customization': customization_settings},
        )
        font_mapping = FontMapping()
        expected = font_mapping.load(
            path=settings.paths.header_font,
            size=font_size,
        )
        font_params = FontParams.from_font(font=expected)
        renderer = PlanRenderer(
            dimensions=Dimensions(rows=1, columns=1),
            settings=settings,
        )

        actual = renderer.get_font(font=font_params)

        assert actual == expected
        font_mapping.clear()

    def test_get_font_by_object(self: Self, font_size: int) -> None:
        """Test getting font by preloaded object.

        :param int font_size: fixture of font size.
        :returns: None
        """
        customization_settings = SETTINGS.customization.model_copy(
            update={'header_font_size': font_size},
        )
        settings = SETTINGS.model_copy(
            update={'customization': customization_settings},
        )
        expected = ImageFont.truetype(
            font=settings.paths.header_font,
            size=font_size,
        )
        font_params = FontParams.from_font(font=expected)
        font_mapping = FontMapping()
        renderer = PlanRenderer(
            dimensions=Dimensions(rows=1, columns=1),
            settings=settings,
        )

        actual = renderer.get_font(font=expected)

        assert actual == expected
        loaded_font = font_mapping[font_params.family][font_params.style][
            font_size
        ]
        assert loaded_font == expected
        font_mapping.clear()
