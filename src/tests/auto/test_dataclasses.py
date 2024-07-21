from typing import Self

from pytest_mock import MockFixture

from src.dataclasses import FontParams


class TestFontParams:
    """Testing dataclass FontParams."""

    def test_from_font(self: Self, mocker: MockFixture) -> None:
        """Test creating FontParams instance from font object.

        :param MockFixture mocker: fixture of mock module.
        :returns: None
        """
        mocked_font = mocker.Mock()
        mocked_font.font.family = 'Family'
        mocked_font.font.style = 'Style'
        mocked_font.size = 999

        dto = FontParams.from_font(font=mocked_font)

        assert dto.family == mocked_font.font.family
        assert dto.style == mocked_font.font.style
        assert dto.size == mocked_font.size
