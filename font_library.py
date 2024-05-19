from types import MappingProxyType

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from constants import FONTS_PATH, FONT_SIZE
from singleton import Singleton


class FontLibrary(metaclass=Singleton):
    """Singleton class that loads fonts and store them. It's singleton to
    prevent multiple loads."""

    def __init__(self) -> None:
        self.__fonts: dict[str, FreeTypeFont] = MappingProxyType(
            {
                path.stem: ImageFont.truetype(font=path, size=FONT_SIZE)
                for path in FONTS_PATH.iterdir()
            },
        )

    def __getitem__(self, item: str) -> FreeTypeFont:
        if not isinstance(item, str):
            raise KeyError(f'Key must be string, got {type(item)}')
        return self.__fonts[item]
