import re
from copy import copy
from pathlib import Path
from typing import Literal, Self
from unittest.mock import Mock

import pytest
from PIL.ImageFont import FreeTypeFont
from pytest_mock import MockFixture

from src.dataclasses import FontParamsForLoading
from src.global_mappings import FontMapping, PlaceholderMapping
from src.settings import SETTINGS


class TestPlaceholderMapping:
    """Testing placeholder mapping."""

    @pytest.mark.usefixtures('_mock_image_contain')
    def test_add(
        self: Self,
        mocked_placeholder: Mock,
        resized_placeholder: Mock,
    ) -> None:
        """Test adding placeholder to mapping.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param Mock resized_placeholder: fixture with mocked resized
         placeholder.
        :returns: None
        """
        mapping = PlaceholderMapping()

        mapping.add(item=mocked_placeholder)

        assert mapping[id(mocked_placeholder)] == resized_placeholder
        mapping.clear()

    def test_add_placeholder_with_same_size_as_cell(
        self: Self,
        mocked_placeholder: Mock,
    ) -> None:
        """Test adding placeholder to mapping with same size as cell.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :returns: None
        """
        mapping = PlaceholderMapping()
        mocked_placeholder.size = (
            SETTINGS.customization.cell_size_without_paddings
        )

        mapping.add(item=mocked_placeholder)

        assert mapping[id(mocked_placeholder)] == mocked_placeholder
        mapping.clear()

    @pytest.mark.usefixtures('_mock_image_contain')
    def test_add_placeholder_already_exists(
        self: Self,
        mocked_placeholder: Mock,
    ) -> None:
        """Test adding placeholder to mapping that already exists.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :returns: None
        """
        expected_msg = 'This image already exists in mapping.'
        mapping = PlaceholderMapping()
        mapping.add(item=mocked_placeholder)

        with pytest.raises(ValueError, match=expected_msg):
            mapping.add(item=mocked_placeholder)

        mapping.clear()

    def test_getitem_negative_size(self: Self) -> None:
        """Test getting placeholder using python syntax with negative size.

        :returns: None
        """
        mapping = PlaceholderMapping()

        with pytest.raises(TypeError):
            _ = mapping[-1]

    @pytest.mark.usefixtures('_mock_image_contain')
    @pytest.mark.parametrize(
        'placeholder_already_exists',
        [False, True],
        ids=('New placeholder', 'Placeholder already exists'),
    )
    def test_get_or_add(
        self: Self,
        mocked_placeholder: Mock,
        resized_placeholder: Mock,
        *,  # Ruff don't let declare boolean position arguments
        placeholder_already_exists: bool,
    ) -> None:
        """Test getting or adding placeholder to mapping.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param Mock resized_placeholder: fixture with mocked resized
         placeholder.
        :param bool placeholder_already_exists: parameter flag to add
         placeholder before testing method get_or_add.
        :returns: None
        """
        mapping = PlaceholderMapping()
        if placeholder_already_exists:
            mapping.add(item=mocked_placeholder)

        actual_placeholder, created = mapping.get_or_add(
            item=mocked_placeholder,
        )

        assert actual_placeholder == resized_placeholder
        assert created != placeholder_already_exists
        mapping.clear()

    @pytest.mark.parametrize(
        'placeholder_already_exists',
        [False, True],
        ids=('New placeholder', 'Placeholder already exists'),
    )
    def test_get_or_add_placeholder_with_same_size_as_cell(
        self: Self,
        mocked_placeholder: Mock,
        *,  # Ruff don't let declare boolean position arguments
        placeholder_already_exists: bool,
    ) -> None:
        """Test getting or adding placeholder to mapping with cell size.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param bool placeholder_already_exists: parameter flag to add
         placeholder before testing method get_or_add.
        :returns: None
        """
        mocked_placeholder.size = (
            SETTINGS.customization.cell_size_without_paddings
        )
        mapping = PlaceholderMapping()
        if placeholder_already_exists:
            mapping.add(item=mocked_placeholder)

        actual_placeholder, created = mapping.get_or_add(
            item=mocked_placeholder,
        )

        assert actual_placeholder == mocked_placeholder
        assert created != placeholder_already_exists
        mapping.clear()

    @pytest.mark.usefixtures('_mock_image_contain')
    def test_clear(self: Self, mocked_placeholder: Mock) -> None:
        """Test clearing mapping.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :returns: None
        """
        mapping = PlaceholderMapping()
        mapping.add(item=mocked_placeholder)

        mapping.clear()

        assert mocked_placeholder not in mapping


class TestFontMapping:
    """Testing font mapping."""

    def test_add(self: Self, mocked_font: Mock) -> None:
        """Test adding font to mapping.

        :param Mock mocked_font: fixture with mocked font.
        :returns: None
        """
        family = mocked_font.font.family
        style = mocked_font.font.style
        size = mocked_font.size
        mapping = FontMapping()

        mapping.add(item=mocked_font)

        assert mapping[family][style][size] == mocked_font
        mapping.clear()

    @pytest.mark.parametrize(
        'exist_key',
        ['family', 'style'],
        ids=(
            'Font with same family already exists',
            'Font with same family and style already exists',
        ),
    )
    def test_add_partial(
        self: Self,
        mocked_font: Mock,
        mocker: MockFixture,
        exist_key: Literal['family', 'style'],
    ) -> None:
        """Test adding font to mapping that family or style already exists.

        :param Mock mocked_font: fixture with mocked font.
        :param MockFixture mocker: fixture of mock module.
        :param Literal['family', 'style'] exist_key: parameter that indicates
         what font parameter is exists.
        :returns: None
        """
        # spec_set not set "font" attribute
        other_font = mocker.Mock(spec=FreeTypeFont)
        other_internal_font = mocker.Mock()  # No spec of internal font
        other_internal_font.family = mocked_font.font.family
        if exist_key == 'style':
            other_internal_font.style = mocked_font.font.style
        else:
            other_internal_font.style = '2'
        other_font.font = other_internal_font
        other_font.size = 999
        mapping = FontMapping()
        mapping.add(item=other_font)
        family = mocked_font.font.family
        style = mocked_font.font.style
        size = mocked_font.size

        mapping.add(item=mocked_font)

        assert mapping[family][style][size] == mocked_font
        mapping.clear()

    def test_add_font_already_exists(self: Self, mocked_font: Mock) -> None:
        """Test adding font that already exists in mapping.

        :param Mock mocked_font: fixture with mocked font.
        :returns: None
        """
        expected_msg = 'This font already exists in mapping.'
        mapping = FontMapping()
        mapping.add(item=mocked_font)

        with pytest.raises(ValueError, match=expected_msg):
            mapping.add(item=mocked_font)

        mapping.clear()

    def test_add_dummy_font(self: Self, mocked_dummy_font: Mock) -> None:
        """Test adding font that already exists in mapping.

        :param Mock mocked_dummy_font: fixture with mocked dummy font.
        :returns: None
        """
        expected_msg = re.escape(
            f'This font have empty family ({mocked_dummy_font.font.family}) '
            f"or style ({mocked_dummy_font.font.style}). It's dummy?",
        )
        mapping = FontMapping()

        with pytest.raises(ValueError, match=expected_msg):
            mapping.add(item=mocked_dummy_font)

    def test_getitem_not_str(self: Self) -> None:
        """Test getting font using python syntax when key is not string..

        :returns: None
        """
        expected_msg = 'Font family must be a string.'
        mapping = FontMapping()

        with pytest.raises(TypeError, match=expected_msg):
            _ = mapping[1]  # type: ignore [index]

    @pytest.mark.parametrize(
        'font_already_exists',
        [False, True],
        ids=('New font', 'Font already exists'),
    )
    def test_add_or_update(
        self: Self,
        mocked_font: Mock,
        mocker: MockFixture,
        *,  # Ruff don't let declare boolean position arguments
        font_already_exists: bool,
    ) -> None:
        """Test adding or updating font to mapping.

        :param Mock mocked_font: fixture with mocked font.
        :param MockFixture mocker: fixture of mock module.
        :param bool font_already_exists: parameter flag to add font before
         testing method add_or_update.
        :returns: None
        """
        mapping = FontMapping()
        if font_already_exists:
            # spec_set not set "font" attribute
            other_font = mocker.Mock(spec=FreeTypeFont)
            other_internal_font = mocker.Mock()  # No spec of internal font
            other_internal_font.family = mocked_font.font.family
            other_internal_font.style = mocked_font.font.style
            other_font.font = other_internal_font
            other_font.size = mocked_font.size
            mapping.add(item=other_font)

        actual_font, added = mapping.add_or_update(item=mocked_font)

        assert actual_font == mocked_font
        assert added != font_already_exists
        mapping.clear()

    @pytest.mark.parametrize(
        ('font_already_exists', 'exist_key'),
        [
            (False, 'family'),
            (False, 'style'),
            (True, 'family'),
            (True, 'style'),
        ],
        ids=(
            'New font, family exists',
            'New font, family and style exists',
            'Font already exists, family exists',
            'Font already exists, family and style exists',
        ),
    )
    def test_add_or_update_partial(
        self: Self,
        mocked_font: Mock,
        mocker: MockFixture,
        exist_key: Literal['family', 'style'],
        *,  # Ruff don't let declare boolean position arguments
        font_already_exists: bool,
    ) -> None:
        """Test adding or updating font that family or style already exists.

        :param Mock mocked_font: fixture with mocked font.
        :param MockFixture mocker: fixture of mock module.
        :param Literal['family', 'style'] exist_key: parameter that indicates
         what font parameter is exists.
        :param bool font_already_exists: parameter flag to add font before
         testing method add_or_update.
        :returns: None
        """
        other_font = mocker.Mock(spec=FreeTypeFont)
        other_internal_font = mocker.Mock()  # No spec of internal font
        other_internal_font.family = mocked_font.font.family
        if exist_key == 'style':
            other_internal_font.style = mocked_font.font.style
        else:
            other_internal_font.style = '2'
        other_font.font = other_internal_font
        other_font.size = 999
        mapping = FontMapping()
        mapping.add(item=other_font)
        if font_already_exists:
            # spec_set not set "font" attribute
            existed_font = mocker.Mock(spec=FreeTypeFont)
            existed_internal_font = mocker.Mock()  # No spec of internal font
            existed_internal_font.family = mocked_font.font.family
            existed_internal_font.style = mocked_font.font.style
            existed_font.font = existed_internal_font
            existed_font.size = mocked_font.size
            mapping.add(item=existed_font)

        actual_font, created = mapping.add_or_update(item=mocked_font)

        assert actual_font == mocked_font
        assert created != font_already_exists
        mapping.clear()

    def test_add_or_update_dummy_font(
        self: Self,
        mocked_dummy_font: Mock,
    ) -> None:
        """Test adding or updating dummy font.

        :param Mock mocked_dummy_font: fixture with mocked dummy font.
        :returns: None
        """
        expected_msg = re.escape(
            f'This font have empty family ({mocked_dummy_font.font.family}) '
            f"or style ({mocked_dummy_font.font.style}). It's dummy?",
        )
        mapping = FontMapping()

        with pytest.raises(ValueError, match=expected_msg):
            mapping.add_or_update(item=mocked_dummy_font)

    @pytest.mark.usefixtures('_mock_font_truetype')
    def test_load(
        self: Self,
        mocked_font: Mock,
        mocked_font_path: Mock,
    ) -> None:
        """Test loading font to mapping from file.

        :param Mock mocked_font: fixture with mocked font.
        :param Mock mocked_font_path: fixture with mocked font path.
        :returns: None
        """
        family = mocked_font.font.family
        style = mocked_font.font.style
        size = mocked_font.size
        font_params = FontParamsForLoading(path=mocked_font_path, size=size)
        mapping = FontMapping()

        mapping.load(font_params=font_params)

        assert mapping[family][style][size] == mocked_font
        assert mocked_font_path in mapping
        mapping.clear()

    def test_load_partial(
        self: Self,
        mocked_font: Mock,
        mocker: MockFixture,
    ) -> None:
        """Test loading font to mapping from file with different size.

        :param Mock mocked_font: fixture with mocked font.
        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mocked_path = mocker.MagicMock(spec_set=Path)
        mocked_path.exists.return_value = True
        mocked_path.suffix = '.ttf'
        mocked_font_other_size = copy(mocked_font)
        # Make sure that size not equal with original mocked font
        other_size = 300
        mocked_font_other_size.size = other_size
        truetype_path = 'PIL.ImageFont.truetype'
        mocker.patch(truetype_path, return_value=mocked_font_other_size)
        mapping = FontMapping()
        font_params_other_size = FontParamsForLoading(
            path=mocked_path,
            size=other_size,
        )
        mapping.load(font_params=font_params_other_size)
        mocker.patch(truetype_path, return_value=mocked_font)
        family = mocked_font.font.family
        style = mocked_font.font.style
        size = mocked_font.size
        font_params = FontParamsForLoading(path=mocked_path, size=size)

        mapping.load(font_params=font_params)

        assert mapping[family][style][other_size] == mocked_font_other_size
        assert mapping[family][style][size] == mocked_font
        assert mocked_path in mapping
        mapping.clear()

    @pytest.mark.usefixtures('_mock_font_truetype')
    def test_clear(
        self: Self,
        mocked_font: Mock,
        mocked_font_path: Mock,
    ) -> None:
        """Test clearing mapping.

        :param Mock mocked_font: fixture with mocked font.
        :param Mock mocked_font_path: fixture with mocked font path.
        :returns: None
        """
        font_params = FontParamsForLoading(
            path=mocked_font_path,
            size=mocked_font.size,
        )
        mapping = FontMapping()
        mapping.load(font_params=font_params)

        mapping.clear()

        assert mocked_font not in mapping
        assert mocked_font_path not in mapping
