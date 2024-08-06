import re
from collections.abc import Sequence
from typing import Self
from unittest.mock import Mock

import pytest
from PIL import ImageDraw
from pytest_mock import MockFixture

from src.dataclasses import FontParams, FontParamsForLoading
from src.enums import StrColor
from src.global_mappings import FontMapping, PlaceholderMapping
from src.renderer import PlanRenderer
from src.schemas import CustomizationSettings, PathSettings, Settings
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
            expected_msg = re.escape(
                f'Object size is out of bounds of box ({object_size} > '
                f'{box_size})',
            )
            with pytest.raises(ValueError, match=expected_msg):
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

    @pytest.mark.integration()
    def test_get_cell_box(
        self: Self,
        plan_cell: PlanCell,
        dimensions: Dimensions,
        mocked_cell_settings: CustomizationSettings,
    ) -> None:
        """Test getting cell box.

        :param PlanCell plan_cell: fixture of plan cell (cell coordinate with
         row and column).
        :param Dimensions dimensions: fixture of dimensions of plan.
        :param CustomizationSettings mocked_cell_settings: fixture with mocked
         customization settings: plan_margins, cell_paddings and cell_size.
        :returns: None
        """
        settings = SETTINGS.model_copy(
            update={'customization': mocked_cell_settings},
        )
        plan_margins = mocked_cell_settings.plan_margins
        cell_paddings = mocked_cell_settings.cell_paddings
        cell_size = mocked_cell_settings.cell_size
        top_no_indents = cell_size.height * plan_cell.row
        left_no_indents = cell_size.width * plan_cell.column
        top = top_no_indents + plan_margins.top + cell_paddings.top
        left = left_no_indents + plan_margins.left + cell_paddings.left
        bottom = top + cell_size.height - cell_paddings.y
        right = left + cell_size.width - cell_paddings.x
        expected = BoxTuple(top=top, right=right, bottom=bottom, left=left)
        renderer = PlanRenderer(dimensions=dimensions, settings=settings)

        result = renderer.get_cell_box(cell=plan_cell)

        assert result == expected

    def test_get_cell_box_not_integration(
        self: Self,
        plan_cell: PlanCell,
        dimensions: Dimensions,
    ) -> None:
        """Test getting cell box with less count of parameters.

        :param PlanCell plan_cell: fixture of plan cell (cell coordinate with
         row and column).
        :param Dimensions dimensions: fixture of dimensions of plan.
        :returns: None
        """
        plan_margins = SETTINGS.customization.plan_margins
        cell_paddings = SETTINGS.customization.cell_paddings
        cell_size = SETTINGS.customization.cell_size
        top_no_indents = cell_size.height * plan_cell.row
        left_no_indents = cell_size.width * plan_cell.column
        top = top_no_indents + plan_margins.top + cell_paddings.top
        left = left_no_indents + plan_margins.left + cell_paddings.left
        bottom = top + cell_size.height - cell_paddings.y
        right = left + cell_size.width - cell_paddings.x
        expected = BoxTuple(top=top, right=right, bottom=bottom, left=left)
        renderer = PlanRenderer(dimensions=dimensions)

        result = renderer.get_cell_box(cell=plan_cell)

        assert result == expected

    def test_get_cell_box_out_of_bounds(self: Self) -> None:
        """Test getting cell box that out of bounds (dimensions).

        :returns: None
        """
        plan_cell = PlanCell(row=9, column=9)
        dimensions = Dimensions(rows=3, columns=5)
        renderer = PlanRenderer(dimensions=dimensions)
        expected_msg = re.escape(
            f'Cell coordinate is out of bounds of this plan (row = '
            f'{plan_cell.row}, column = {plan_cell.column}, {dimensions})',
        )

        with pytest.raises(ValueError, match=expected_msg):
            renderer.get_cell_box(cell=plan_cell)

    @pytest.mark.usefixtures('_mock_font_truetype')
    def test_get_font(
        self: Self,
        font_param_to_get_font: FontParams | FontParamsForLoading | Mock,
        mocked_font: Mock,
        mocked_path_settings: PathSettings,
    ) -> None:
        """Test getting font.

        :param FontParams | FontParamsForLoading | Mock font_param_to_get_font:
         fixture with font parameter that will pass to method.
        :param Mock mocked_font: fixture with mocked font.
        :param PathSettings mocked_path_settings: fixture with mocked path
         settings.
        :returns: None
        """
        settings = SETTINGS.model_copy(update={'path': mocked_path_settings})
        font_mapping = FontMapping()
        renderer = PlanRenderer(
            dimensions=Dimensions(rows=1, columns=1),
            settings=settings,
        )

        actual = renderer.get_font(font=font_param_to_get_font)

        assert actual == mocked_font
        font_mapping.clear()

    def test_get_font_by_params_that_does_not_exist(
        self: Self,
        mocked_font: Mock,
    ) -> None:
        """Test getting font that does not exist by parameters.

        :param Mock mocked_font: fixture with mocked font.
        :returns: None
        """
        font_params = FontParams.from_font(font=mocked_font)
        expected_msg = (
            f'Font {font_params.family} {font_params.style} with size '
            f'{font_params.size} not found'
        )
        renderer = PlanRenderer(dimensions=Dimensions(rows=1, columns=1))

        with pytest.raises(ValueError, match=expected_msg):
            _ = renderer.get_font(font=font_params)

    def test_get_font_by_unexpected_type(self: Self) -> None:
        """Test getting font by unexpected type.

        :returns: None
        """
        param = 'test'
        expected_msg = f'Unsupported type for getting font: {type(param)}'
        renderer = PlanRenderer(dimensions=Dimensions(rows=1, columns=1))

        with pytest.raises(TypeError, match=expected_msg):
            _ = renderer.get_font(font=param)  # type: ignore [arg-type]

    @pytest.mark.usefixtures('_mock_textbbox_method')
    def test_get_textbox_size(
        self: Self,
        mocked_font: Mock,
        mocked_textbox_size: Size,
    ) -> None:
        """Testing getting textbox size.

        :param Mock mocked_font: fixture with mocked font.
        :param Size mocked_textbox_size: fixture with mocked textbox size.
        :returns: None
        """
        text = 'Test'
        renderer = PlanRenderer(dimensions=Dimensions(rows=1, columns=1))

        actual = renderer.get_textbox_size(text=text, font=mocked_font)

        assert actual == mocked_textbox_size

    @pytest.mark.usefixtures('_mock_drawing_text')
    @pytest.mark.parametrize(
        'textbox_deductibles',
        [(0, 0), (5, 0), (0, 6), (4, 6)],
        ids=(
            'Textbox equal box where need to draw',
            'Textbox width smaller than box where need to draw',
            'Textbox height smaller than box where need to draw',
            'Textbox smaller in both dimensions than box where need to draw',
        ),
    )
    def test_draw_text_in_box(
        self: Self,
        box_tuple: BoxTuple,
        mocked_font: Mock,
        mocker: MockFixture,
        textbox_deductibles: tuple[int, int],
    ) -> None:
        """Testing drawing text in box.

        As this method returns None, this test checks that this method not
        fails.
        :param BoxTuple box_tuple: fixture of box coordinates inside which need
         draw text.
        :param Mock mocked_font: fixture with mocked font.
        :param MockFixture mocker: fixture of mock module.
        :param tuple[int, int] textbox_deductibles: parameter with deductibles
         from box_tuple size for textbox size.
        :returns: None
        """
        # This is only test where need sync textbox size with box_tuple, so
        # textbbox method mocks here manually
        width_deductible, height_deductible = textbox_deductibles
        textbox_size = Size(
            width=box_tuple.size.width - width_deductible,
            height=box_tuple.size.height - height_deductible,
        )
        mocker.patch(
            'PIL.ImageDraw.ImageDraw.textbbox',
            return_value=(0, 0, *textbox_size),
            spec_set=ImageDraw.ImageDraw.textbbox,
        )
        text = 'Test'
        color = StrColor.WHITE
        renderer = PlanRenderer(dimensions=Dimensions(rows=1, columns=1))

        renderer.draw_text_in_box(
            text=text,
            font=mocked_font,
            color=color,
            box=box_tuple,
        )

    @pytest.mark.integration()
    @pytest.mark.usefixtures(
        '_mock_textbbox_method',
        '_mock_font_truetype',
        '_mock_drawing_text',
    )
    def test_draw_header(
        self: Self,
        dimensions: Dimensions,
        font_param: FontParams | FontParamsForLoading | Mock | None,
        mocked_renderer_settings: Settings,
    ) -> None:
        """Testing drawing header.

        As this method returns None, this test checks that this method not
        fails.
        :param Dimensions dimensions: fixture of dimensions of plan.
        :param FontParams | FontParamsForLoading | Mock | None font_param:
         fixture with font parameter that will pass to method.
        :param Settings mocked_renderer_settings: fixture with mocked settings:
         paths to fonts, plan_margins, cell_paddings and cell_size.
        :returns: None
        """
        headers = tuple(str(num) for num in range(dimensions.columns))
        font_mapping = FontMapping()
        renderer = PlanRenderer(
            dimensions=dimensions,
            settings=mocked_renderer_settings,
        )

        renderer.draw_header(headers=headers, font=font_param)

        font_mapping.clear()

    @pytest.mark.usefixtures(
        '_mock_textbbox_method',
        '_mock_font_truetype',
        '_mock_drawing_text',
    )
    def test_draw_header_not_integration(
        self: Self,
        mocked_path_settings: PathSettings,
        cell_paddings: BoxTuple,
        cell_size: Size,
    ) -> None:
        """Testing drawing header with small count of parameters.

        As this method returns None, this test checks that this method not
        fails.
        :param PathSettings mocked_path_settings: fixture with mocked path
         settings.
        :param BoxTuple cell_paddings: fixture with cell paddings.
        :param Size cell_size: fixture with cell size.
        :returns: None
        """
        customization_settings = SETTINGS.customization.model_copy(
            update={'cell_size': cell_size, 'cell_paddings': cell_paddings},
        )
        settings = SETTINGS.model_copy(
            update={
                'path': mocked_path_settings,
                'customization': customization_settings,
            },
        )
        dimensions = Dimensions(rows=6, columns=7)
        headers = tuple(str(num) for num in range(dimensions.columns))
        font_mapping = FontMapping()
        renderer = PlanRenderer(dimensions=dimensions, settings=settings)

        renderer.draw_header(headers=headers)

        font_mapping.clear()

    @pytest.mark.usefixtures('_mock_font_truetype')
    @pytest.mark.parametrize(
        'headers',
        [('1',), ('1', '2', '3')],
        ids=('Count headers < count columns', 'Count headers > count columns'),
    )
    def test_draw_header_headers_count_not_equal_count_columns(
        self: Self,
        mocked_path_settings: PathSettings,
        headers: Sequence[str],
    ) -> None:
        """Testing drawing header when count headers not equal count columns.

        :param PathSettings mocked_path_settings: fixture with mocked path
         settings.
        :param Sequence[str] headers: parameter with headers.
        :returns: None
        """
        settings = SETTINGS.model_copy(update={'path': mocked_path_settings})
        dimensions = Dimensions(rows=6, columns=2)
        expected_msg = f'Count headers must be 2, but got {len(headers)}'
        font_mapping = FontMapping()
        renderer = PlanRenderer(dimensions=dimensions, settings=settings)

        with pytest.raises(ValueError, match=expected_msg):
            renderer.draw_header(headers=headers)

        font_mapping.clear()

    @pytest.mark.integration()
    @pytest.mark.usefixtures(
        '_mock_textbbox_method',
        '_mock_font_truetype',
        '_mock_drawing_text',
        '_mock_image_contain_to_allowable_cell_size',
        '_mock_image_paste',
    )
    def test_draw_plan(
        self: Self,
        dimensions: Dimensions,
        mocked_placeholder: Mock,
        font_param: FontParams | FontParamsForLoading | Mock | None,
        mocked_renderer_settings: Settings,
        start_from_column: int,
    ) -> None:
        """Test drawing plan.

        As this method returns None, this test checks that this method not
        fails.
        :param Dimensions dimensions: fixture of dimensions of plan.
        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param FontParams | FontParamsForLoading | Mock | None font_param:
         fixture with font parameter that will pass to method.
        :param Settings mocked_renderer_settings: fixture with mocked settings:
         paths to fonts, plan_margins, cell_paddings and cell_size.
        :param int start_from_column: fixture with column index where need to
         start draw plan.
        :returns: None
        """
        placeholder_mapping = PlaceholderMapping()
        font_mapping = FontMapping()
        max_elements = dimensions.rows * dimensions.columns
        count_elements = max_elements - start_from_column
        elements = tuple(str(num) for num in range(count_elements))
        placeholders = tuple(mocked_placeholder for _ in range(count_elements))
        renderer = PlanRenderer(
            dimensions=dimensions,
            settings=mocked_renderer_settings,
        )

        renderer.draw_plan(
            elements=elements,
            placeholders=placeholders,
            font=font_param,
            start_from_column=start_from_column,
        )

        placeholder_mapping.clear()
        font_mapping.clear()

    @pytest.mark.usefixtures(
        '_mock_textbbox_method',
        '_mock_font_truetype',
        '_mock_drawing_text',
        '_mock_image_contain_to_allowable_cell_size',
        '_mock_image_paste',
    )
    def test_draw_plan_not_integration(
        self: Self,
        mocked_path_settings: PathSettings,
        mocked_placeholder: Mock,
        cell_paddings: BoxTuple,
        cell_size: Size,
    ) -> None:
        """Test drawing plan with small count of parameters.

        As this method returns None, this test checks that this method not
        fails.
        :param PathSettings mocked_path_settings: fixture with mocked path
         settings.
        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param BoxTuple cell_paddings: fixture with cell paddings.
        :param Size cell_size: fixture with cell size.
        :returns: None
        """
        customization_settings = SETTINGS.customization.model_copy(
            update={'cell_size': cell_size, 'cell_paddings': cell_paddings},
        )
        settings = SETTINGS.model_copy(
            update={
                'path': mocked_path_settings,
                'customization': customization_settings,
            },
        )
        dimensions = Dimensions(rows=6, columns=7)
        placeholder_mapping = PlaceholderMapping()
        font_mapping = FontMapping()
        count_elements = dimensions.rows * dimensions.columns
        elements = tuple(str(num) for num in range(count_elements))
        placeholders = tuple(mocked_placeholder for _ in range(count_elements))
        renderer = PlanRenderer(dimensions=dimensions, settings=settings)

        renderer.draw_plan(elements=elements, placeholders=placeholders)

        placeholder_mapping.clear()
        font_mapping.clear()

    def test_draw_plan_count_elements_not_equal(
        self: Self,
        mocked_placeholder: Mock,
    ) -> None:
        """Test drawing plan when count elements not equal placeholders.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :returns: None
        """
        dimensions = Dimensions(rows=6, columns=7)
        placeholder_mapping = PlaceholderMapping()
        font_mapping = FontMapping()
        elements = tuple(str(num) for num in range(3))
        placeholders = tuple(mocked_placeholder for _ in range(4))
        renderer = PlanRenderer(dimensions=dimensions)
        expected_msg = (
            'Sequences of elements and placeholders must have same size.'
        )

        with pytest.raises(ValueError, match=expected_msg):
            renderer.draw_plan(elements=elements, placeholders=placeholders)

        placeholder_mapping.clear()
        font_mapping.clear()

    @pytest.mark.parametrize(
        'start_from_column',
        [-1, 8],
        ids=(
            'Start drawing from negative column',
            'Start drawing from column that out of bounds of plan',
        ),
    )
    def test_draw_plan_start_from_column_out_of_bounds(
        self: Self,
        mocked_placeholder: Mock,
        start_from_column: int,
    ) -> None:
        """Test drawing plan when start_from_column is out of bounds of plan.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param int start_from_column: parameter that indicates where start draw
         plan.
        :returns: None
        """
        dimensions = Dimensions(rows=6, columns=7)
        placeholder_mapping = PlaceholderMapping()
        font_mapping = FontMapping()
        count_elements = dimensions.rows * dimensions.columns
        elements = tuple(str(num) for num in range(count_elements))
        placeholders = tuple(mocked_placeholder for _ in range(count_elements))
        renderer = PlanRenderer(dimensions=dimensions)
        expected_msg = 'Column index must be between 0 and 7.'

        with pytest.raises(ValueError, match=expected_msg):
            renderer.draw_plan(
                elements=elements,
                placeholders=placeholders,
                start_from_column=start_from_column,
            )

        placeholder_mapping.clear()
        font_mapping.clear()
