from typing import Self
from unittest.mock import Mock

import pytest

from src.dataclasses import FontParams


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
        with pytest.raises(ValueError):
            _ = FontParams.from_font(font=mocked_dummy_font)
