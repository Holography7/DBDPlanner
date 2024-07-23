import itertools
from collections.abc import Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any, ClassVar, Literal, Self

import pytest

from src.enums import StrColor
from src.exceptions import SettingsParsingError
from src.settings_parser import SettingsParser
from src.tests.utils import product_str
from src.types import BoxTuple, RGBColor, Size
from src.utils import correct_paths


class TestSettingsParser:
    """Testing parser of settings."""

    DATA: ClassVar[dict[str, dict[str, Any]]] = {
        'paths': {
            'header_font': 'fonts/OpenSans-Regular.ttf',
            'body_font': 'fonts/OpenSans-Regular.ttf',
            'placeholders': 'images',
            'plans': 'plans',
        },
        'customization': {
            'header_font_size': 108,
            'body_font_size': 34,
            'header_text_color': StrColor.WHITE,
            'body_text_color': StrColor.RED,
            'background_color': StrColor.BLACK,
            # for margins and paddings you must always set 4 values. That needs
            # to convert this values to other formats correctly
            'plan_margins': [30, 80, 100, 50],
            # for paddings first and second value must be lower than half of
            # cell size for x and y.
            'cell_paddings': [20, 40, 70, 30],
            'cell_size': [360, 360],
            'resampling_method': 'Lanczos',
        },
    }
    WRONG_DATA: ClassVar[dict[str, dict[str, Any]]] = {
        'paths': {
            'header_font': 'wrong.ttf',
            'body_font': 'wrong.ttf',
            'placeholders': 'wrong',
            'plans': 'wrong',
        },
        'customization': {
            'header_font_size': -1,
            'body_font_size': -2,
            'header_text_color': 'wrong',
            'body_text_color': 'wrong',
            'background_color': 'wrong',
            'plan_margins': [-1, -2, -3, -4],
            'cell_paddings': [-1, -2, -3, -4],
            'cell_size': [-5, -6],
            'resampling_method': 'wrong',
        },
    }
    ERRORS: ClassVar[set[str]] = {
        'paths.header_font',
        'paths.body_font',
        'paths.placeholders',
        'paths.plans',
        'customization.header_font_size',
        'customization.body_font_size',
        'customization.header_text_color.call[RGBColor]',
        'customization.header_text_color.str-enum[StrColor]',
        'customization.body_text_color.call[RGBColor]',
        'customization.body_text_color.str-enum[StrColor]',
        'customization.background_color.call[RGBColor]',
        'customization.background_color.str-enum[StrColor]',
        'customization.plan_margins.0',
        'customization.plan_margins.1',
        'customization.plan_margins.2',
        'customization.plan_margins.3',
        'customization.cell_paddings.0',
        'customization.cell_paddings.1',
        'customization.cell_paddings.2',
        'customization.cell_paddings.3',
        'customization.cell_size.0',
        'customization.cell_size.1',
        'customization.resampling_method',
    }
    RGB_COLORS: ClassVar[dict[str, Sequence[int]]] = {
        StrColor.WHITE: [255, 255, 255],
        StrColor.BLACK: [0, 0, 0],
        StrColor.RED: [255, 0, 0],
    }
    COLOR_FIELDS: ClassVar[Sequence[str]] = (
        'header_text_color',
        'body_text_color',
        'background_color',
    )
    BOX_FIELDS: ClassVar[Sequence[str]] = (
        'plan_margins',
        'cell_paddings',
    )

    def set_box_values(
        self: Self,
        customization: dict[str, Any],
        count_numbers: int,
    ) -> None:
        """Set box values as list with len = count_numbers or integer.

        If count_numbers = 0, then will set as integer.
        :param dict[str, Any] customization: dict with customization
         settings.
        :param int count_numbers: count elements in list. If zero, then it will
         set as integer.
        :returns: None
        """
        if count_numbers == 0:
            for box_field in self.BOX_FIELDS:
                customization[box_field] = customization[box_field][0]
        else:
            for box_field in self.BOX_FIELDS:
                sliced = customization[box_field][0:count_numbers]
                customization[box_field] = sliced

    def get_expected_customization_data(
        self: Self,
        raw: dict[str, Any],
    ) -> dict[str, Any]:
        """Help method to get expected customization data for testing.

        :param dict[str, Any] raw: initial data of customization.
        :returns: dict with expected customization data.
        """
        header_text_color = self.get_expected_color(raw['header_text_color'])
        body_text_color = self.get_expected_color(raw['body_text_color'])
        background_color = self.get_expected_color(raw['background_color'])
        plan_margins = self.get_expected_box_tuple(raw['plan_margins'])
        cell_paddings = self.get_expected_box_tuple(raw['cell_paddings'])
        return {
            'header_font_size': raw['header_font_size'],
            'body_font_size': raw['body_font_size'],
            'header_text_color': header_text_color,
            'body_text_color': body_text_color,
            'background_color': background_color,
            'plan_margins': plan_margins,
            'cell_paddings': cell_paddings,
            'cell_size': Size(*raw['cell_size']),
        }

    @staticmethod
    def get_expected_color(value: str | Sequence[int]) -> str | RGBColor:
        """Get expected color for testing.

        :param str | Sequence[int] value: initial value.
        :returns: color string or RGBColor instance.
        """
        if isinstance(value, str):
            return value
        return RGBColor(*value)

    def get_expected_box_tuple(
        self: Self,
        value: int | Sequence[int],
    ) -> BoxTuple:
        """Get expected BoxTuple for testing.

        :param str | Sequence[int] value: initial value.
        :returns: BoxTuple instance.
        """
        if isinstance(value, int):
            return BoxTuple(top=value, right=value, bottom=value, left=value)
        return self.transform_tuple_to_box_tuple(value=value)

    @staticmethod
    def transform_tuple_to_box_tuple(value: Sequence[int]) -> BoxTuple:
        """Transform sequence to BoxTuple.

        :param Sequence[int] value: initial value.
        :returns: BoxTuple instance.
        """
        match len(value):
            case 1:
                return BoxTuple(
                    top=value[0],
                    right=value[0],
                    bottom=value[0],
                    left=value[0],
                )
            case 2:
                return BoxTuple(
                    top=value[0],
                    right=value[1],
                    bottom=value[0],
                    left=value[1],
                )
            case 3:
                return BoxTuple(
                    top=value[0],
                    right=value[1],
                    bottom=value[2],
                    left=value[1],
                )
            case 4:
                return BoxTuple(
                    top=value[0],
                    right=value[1],
                    bottom=value[2],
                    left=value[3],
                )
            case _:
                msg = f'Unexpected len of value: {len(value)}, max is 4'
                raise ValueError(msg)

    @pytest.mark.parametrize(
        ('color_format', 'count_box_numbers'),
        itertools.product(('HTML', 'RGB'), range(5)),
        ids=product_str(
            ('Color is HTML word', 'Color is RGB'),
            tuple(
                f'Paddings and margins is {box_format}'
                for box_format in (
                    'integer',
                    *(f'list with {count} integers' for count in range(1, 5)),
                )
            ),
        ),
    )
    def test_parse_data(
        self: Self,
        color_format: Literal['HTML', 'RGB'],
        count_box_numbers: int,
    ) -> None:
        """Testing parsing settings from dict.

        :param Literal['HTML', 'RGB'] color_format: color format.
        :param int count_box_numbers: count numbers in box settings. If zero,
         then it will be as integer.
        :returns: None
        """
        data = deepcopy(self.DATA)
        # You could run this test from not project root, so need change paths
        # to pass path validation
        data['paths'] = correct_paths(initial=data['paths'])
        # Change format of some fields
        if color_format == 'RGB':
            for color_field in self.COLOR_FIELDS:
                rgb_value = self.RGB_COLORS[data['customization'][color_field]]
                data['customization'][color_field] = rgb_value
        self.set_box_values(
            customization=data['customization'],
            count_numbers=count_box_numbers,
        )
        # prepare expected data
        expected = {
            **{key: Path(value) for key, value in data['paths'].items()},
            **self.get_expected_customization_data(raw=data['customization']),
        }

        settings = SettingsParser.parse_data(data=data)

        # assert paths
        paths = settings.paths
        assert paths.header_font == expected['header_font']
        assert paths.body_font == expected['body_font']
        assert paths.placeholders == expected['placeholders']
        assert paths.plans == expected['plans']
        # assert customization settings
        customization = settings.customization
        assert customization.header_font_size == expected['header_font_size']
        assert customization.body_font_size == expected['body_font_size']
        assert customization.header_text_color == expected['header_text_color']
        assert customization.body_text_color == expected['body_text_color']
        assert customization.background_color == expected['background_color']
        assert customization.plan_margins == expected['plan_margins']
        assert customization.cell_paddings == expected['cell_paddings']
        assert customization.cell_size == expected['cell_size']

    def test_parse_wrong_data(self: Self) -> None:
        """Testing parsing settings from dict with wrong data.

        :returns: None
        """
        expected_errors = deepcopy(self.ERRORS)

        with pytest.raises(SettingsParsingError) as exc:
            SettingsParser.parse_data(data=self.WRONG_DATA)

        actual_errors: set[str] = {
            error.split(':', maxsplit=1)[0] for error in exc.value.errors
        }
        assert actual_errors == expected_errors

    @pytest.mark.parametrize(
        'cell_paddings',
        (
            [300, 0, 0, 0],
            [0, 300, 0, 0],
            [0, 0, 300, 0],
            [0, 0, 0, 300],
            [299, 0, 1, 0],
            [0, 299, 0, 1],
            [1, 0, 299, 0],
            [0, 1, 0, 299],
            150,
            [150],
            [150, 0],
            [0, 150],
            [300, 0, 0],
            [0, 150, 0],
            [0, 0, 300],
            [299, 0, 1],
            [1, 0, 299],
        ),
        ids=(
            'Top is huge',
            'Right is huge',
            'Bottom is huge',
            'Left is huge',
            'Sum of Y is huge (top)',
            'Sum of X is huge (right)',
            'Sum of Y is huge (bottom)',
            'Sum of X is huge (left)',
            'Integer equal half cell size',
            'List with 1 element equal half cell size',
            'List with 2 elements, Y equal half cell size',
            'List with 2 elements, X equal half cell size',
            'List with 3 elements, top is huge',
            'List with 3 elements, X equal half cell size',
            'List with 3 elements, bottom is huge',
            'List with 3 elements, Y is huge (top)',
            'List with 3 elements, Y is huge (bottom)',
        ),
    )
    def test_parse_huge_paddings(
        self: Self,
        cell_paddings: list[int] | int,
    ) -> None:
        """Test parsing settings from dict if paddings bigger than cell size.

        :returns: None
        """
        data = deepcopy(self.DATA)
        # You could run this test from not project root, so need change paths
        # to pass path validation
        data['paths'] = correct_paths(initial=data['paths'])
        data['customization']['cell_paddings'] = cell_paddings
        data['customization']['cell_size'] = (300, 300)

        with pytest.raises(SettingsParsingError) as exc:
            SettingsParser.parse_data(data=data)

        actual_errors: set[str] = {
            error.split(':', maxsplit=1)[0] for error in exc.value.errors
        }
        assert actual_errors == {'customization'}

    def test_load_settings_from_not_toml(self: Self) -> None:
        """Testing that method "load_settings_from_toml" raise exception.

        It raises when setting file is not toml extension.
        :returns: None
        """
        with pytest.raises(ValueError):
            SettingsParser.load_settings_from_toml(path=Path('not_toml.txt'))
