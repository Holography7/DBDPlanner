from pathlib import Path
from typing import Literal, Self
from unittest.mock import Mock

import pytest
from PIL.ImageFont import FreeTypeFont
from pytest_mock import MockFixture

from src.global_mappings import FontMapping, PlaceholderMapping


class TestPlaceholderMapping:
    """Testing placeholder mapping."""

    def test_add(
        self: Self,
        mocked_placeholder: Mock,
        resized_placeholder: Mock,
        mocker: MockFixture,
    ) -> None:
        """Test adding placeholder to mapping.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param Mock resized_placeholder: fixture with mocked resized
         placeholder.
        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mapping = PlaceholderMapping()
        mocker.patch('PIL.ImageOps.contain', return_value=resized_placeholder)
        if mocked_placeholder.size == resized_placeholder.size:
            expected_placeholder = mocked_placeholder
        else:
            expected_placeholder = resized_placeholder

        mapping.add(item=mocked_placeholder)

        assert mapping[id(mocked_placeholder)] == expected_placeholder
        mapping.clear()

    def test_add_placeholder_already_exists(
        self: Self,
        mocked_placeholder: Mock,
        resized_placeholder: Mock,
        mocker: MockFixture,
    ) -> None:
        """Test adding placeholder to mapping that already exists.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param Mock resized_placeholder: fixture with mocked resized
         placeholder.
        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mapping = PlaceholderMapping()
        mocker.patch('PIL.ImageOps.contain', return_value=resized_placeholder)
        mapping.add(item=mocked_placeholder)

        with pytest.raises(ValueError):
            mapping.add(item=mocked_placeholder)

        mapping.clear()

    def test_getitem_negative_size(self: Self) -> None:
        """Test getting placeholder using python syntax with negative size.

        :returns: None
        """
        mapping = PlaceholderMapping()

        with pytest.raises(TypeError):
            _ = mapping[-1]

    @pytest.mark.parametrize(
        'placeholder_already_exists',
        (False, True),
        ids=('New placeholder', 'Placeholder already exists'),
    )
    def test_get_or_add(
        self: Self,
        mocked_placeholder: Mock,
        resized_placeholder: Mock,
        mocker: MockFixture,
        *,  # Ruff don't let declare boolean position arguments
        placeholder_already_exists: bool,
    ) -> None:
        """Test getting or adding placeholder to mapping.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param Mock resized_placeholder: fixture with mocked resized
         placeholder.
        :param MockFixture mocker: fixture of mock module.
        :param bool placeholder_already_exists: parameter flag to add
         placeholder before testing method get_or_add.
        :returns: None
        """
        mapping = PlaceholderMapping()
        mocker.patch('PIL.ImageOps.contain', return_value=resized_placeholder)
        if placeholder_already_exists:
            mapping.add(item=mocked_placeholder)
        if mocked_placeholder.size == resized_placeholder.size:
            expected_placeholder = mocked_placeholder
        else:
            expected_placeholder = resized_placeholder

        actual_placeholder, created = mapping.get_or_add(
            item=mocked_placeholder,
        )

        assert actual_placeholder == expected_placeholder
        assert created != placeholder_already_exists
        mapping.clear()

    def test_clear(
        self: Self,
        mocked_placeholder: Mock,
        resized_placeholder: Mock,
        mocker: MockFixture,
    ) -> None:
        """Test clearing mapping.

        :param Mock mocked_placeholder: fixture with mocked placeholder.
        :param Mock resized_placeholder: fixture with mocked resized
         placeholder.
        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mapping = PlaceholderMapping()
        mocker.patch('PIL.ImageOps.contain', return_value=resized_placeholder)
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
        ('family', 'style'),
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
        mapping = FontMapping()
        mapping.add(item=mocked_font)

        with pytest.raises(ValueError):
            mapping.add(item=mocked_font)

        mapping.clear()

    def test_add_dummy_font(self: Self, mocked_dummy_font: Mock) -> None:
        """Test adding font that already exists in mapping.

        :param Mock mocked_dummy_font: fixture with mocked dummy font.
        :returns: None
        """
        mapping = FontMapping()

        with pytest.raises(ValueError):
            mapping.add(item=mocked_dummy_font)

    def test_getitem_not_str(self: Self) -> None:
        """Test getting font using python syntax when key is not string..

        :returns: None
        """
        mapping = FontMapping()

        with pytest.raises(TypeError):
            _ = mapping[1]  # type: ignore [index]

    @pytest.mark.parametrize(
        'font_already_exists',
        (False, True),
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
        (
            (False, 'family'),
            (False, 'style'),
            (True, 'family'),
            (True, 'style'),
        ),
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
        mapping = FontMapping()

        with pytest.raises(ValueError):
            mapping.add_or_update(item=mocked_dummy_font)

    def test_load(
        self: Self,
        mocked_font: Mock,
        mocker: MockFixture,
    ) -> None:
        """Test loading font to mapping from file.

        :param Mock mocked_font: fixture with mocked font.
        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mocked_path = mocker.MagicMock(spec_set=Path)
        mocked_path.exists.return_value = True
        mocked_path.suffix = '.ttf'
        mocker.patch('PIL.ImageFont.truetype', return_value=mocked_font)
        family = mocked_font.font.family
        style = mocked_font.font.style
        size = mocked_font.size
        mapping = FontMapping()

        mapping.load(path=mocked_path, size=mocked_font.size)

        assert mapping[family][style][size] == mocked_font
        assert mocked_path in mapping
        mapping.clear()

    def test_load_file_not_exists(self: Self, mocker: MockFixture) -> None:
        """Test loading font to mapping from file that does not exist.

        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mocked_path = mocker.MagicMock(spec_set=Path)
        mocked_path.exists.return_value = False
        mapping = FontMapping()

        with pytest.raises(FileNotFoundError):
            mapping.load(path=mocked_path, size=1)

    def test_load_not_ttf(self: Self, mocker: MockFixture) -> None:
        """Test loading font to mapping from not ttf file.

        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mocked_path = mocker.MagicMock(spec_set=Path)
        mocked_path.exists.return_value = True
        mapping = FontMapping()

        with pytest.raises(ValueError):
            mapping.load(path=mocked_path, size=1)

    def test_clear(self: Self, mocked_font: Mock) -> None:
        """Test clearing mapping.

        :returns: None
        """
        mapping = FontMapping()
        mapping.add(item=mocked_font)

        mapping.clear()

        assert mocked_font not in mapping
