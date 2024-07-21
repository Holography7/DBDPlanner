from dataclasses import dataclass
from typing import Self

from PIL.ImageFont import FreeTypeFont


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
        return cls(
            family=font.font.family,
            style=font.font.style,
            size=font.size,
        )
