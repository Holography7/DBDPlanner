from types import MappingProxyType
from typing import Self

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from constants import FONT_SIZE, FONTS_PATH
from singleton import Singleton


class FontLibrary(metaclass=Singleton):
    """Singleton class that loads fonts and store them.

    Singleton required to prevent multiple loads.
    """

    def __init__(self: Self) -> None:
        """Initialize fonts."""
        self.__fonts: dict[str, FreeTypeFont] = MappingProxyType(
            {
                path.stem: ImageFont.truetype(font=path, size=FONT_SIZE)
                for path in FONTS_PATH.iterdir()
            },
        )

    def __getitem__(self: Self, item: str) -> FreeTypeFont:
        """Get font."""
        if not isinstance(item, str):
            msg = f'Key must be string, got {type(item)}'
            raise KeyError(msg)
        return self.__fonts[item]


FONT_LIBRARY = FontLibrary()
