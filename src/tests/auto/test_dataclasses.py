import re
from pathlib import Path
from typing import Self
from unittest.mock import Mock

import pytest
from pytest_mock import MockFixture

from src.constants import FONT_EXTENSION
from src.dataclasses import FontParams, FontParamsForLoading


class TestFontParams:
    """Testing dataclass FontParams."""

    def test_from_font(self: Self, mocked_font: Mock) -> None:
        """Test creating FontParams from font.

        :param Mock mocked_font: fixture with mocked font.
        :returns: None
        """
        dto = FontParams.from_font(font=mocked_font)

        assert dto.family == mocked_font.font.family
        assert dto.style == mocked_font.font.style
        assert dto.size == mocked_font.size

    def test_from_font_dummy(self: Self, mocked_dummy_font: Mock) -> None:
        """Test creating FontParams from font with empty family and style.

        :param Mock mocked_dummy_font: fixture with mocked dummy font.
        :returns: None
        """
        expected_msg = re.escape(
            f'This font have empty family ({mocked_dummy_font.font.family}) '
            f"or style ({mocked_dummy_font.font.style}). It's dummy?",
        )

        with pytest.raises(ValueError, match=expected_msg):
            _ = FontParams.from_font(font=mocked_dummy_font)


class TestFontParamsForLoading:
    """Testing dataclass for loading font from disk."""

    def test_file_not_exists(self: Self, mocker: MockFixture) -> None:
        """Test creating DTO if file that does not exist.

        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mocked_path = mocker.MagicMock(spec_set=Path)
        mocked_path.exists.return_value = False
        expected_msg = f'Font does not exists: {mocked_path}'

        with pytest.raises(FileNotFoundError, match=expected_msg):
            FontParamsForLoading(path=mocked_path, size=1)

    def test_not_ttf(self: Self, mocker: MockFixture) -> None:
        """Test creating DTO if file is not .ttf.

        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mocked_path = mocker.MagicMock(spec_set=Path)
        mocked_path.exists.return_value = True
        expected_msg = (
            f'Only "{FONT_EXTENSION}" allowed, got {mocked_path.suffix}'
        )

        with pytest.raises(ValueError, match=expected_msg):
            FontParamsForLoading(path=mocked_path, size=1)
