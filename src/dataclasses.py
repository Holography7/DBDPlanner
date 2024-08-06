from dataclasses import dataclass
from pathlib import Path
from typing import Self

from PIL.ImageFont import FreeTypeFont

from src.constants import FONT_EXTENSION


@dataclass
class FontParams:
    """Dataclass of font parameters."""

    family: str
    style: str
    size: float

    @classmethod
    def from_font(cls: type[Self], font: FreeTypeFont) -> Self:
        """Create dataclass from font object.

        :param FreeTypeFont font: font object.
        :returns: FontParams dataclass.
        """
        if not font.font.family or not font.font.style:
            # Real reason unknown, problem detected by mypy
            msg = (
                f'This font have empty family ({font.font.family}) or style '
                f"({font.font.style}). It's dummy?"
            )
            raise ValueError(msg)
        return cls(
            family=font.font.family,
            style=font.font.style,
            size=font.size,
        )


@dataclass
class FontParamsForLoading:
    """Dataclass of font parameters for loading from disk.

    File must exist and with .ttf extension.
    """

    path: Path
    size: float

    def __post_init__(self: Self) -> None:
        """Validate that path exists and desires to .ttf font.

        :returns: None
        """
        if not self.path.exists():
            msg = f'Font does not exists: {self.path}'
            raise FileNotFoundError(msg)
        if self.path.suffix != FONT_EXTENSION:
            msg = f'Only "{FONT_EXTENSION}" allowed, got {self.path.suffix}'
            raise ValueError(msg)
