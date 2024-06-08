from types import MappingProxyType
from typing import TYPE_CHECKING, Self

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont

from src.schemas import Settings
from src.settings import SETTINGS
from src.singleton import Singleton

if TYPE_CHECKING:
    from collections.abc import Mapping

    from src.types import FontParams


class FontLibrary(metaclass=Singleton):
    """Singleton class that loads fonts and store them.

    Singleton required to prevent multiple loads.
    """

    def __init__(self: Self, settings: Settings = SETTINGS) -> None:
        """Initialize fonts.

        :param Settings settings: pydantic model with settings.
        :returns: None
        """
        fonts_params: tuple[FontParams, ...] = (
            {
                'font': settings.paths.header_font,
                'size': settings.customization.header_font_size,
            },
            {
                'font': settings.paths.body_font,
                'size': settings.customization.body_font_size,
            },
        )
        self.__fonts: Mapping[str, FreeTypeFont] = MappingProxyType(
            {
                font_params['font'].stem: ImageFont.truetype(**font_params)
                for font_params in fonts_params
            },
        )

    def __getitem__(self: Self, item: str) -> FreeTypeFont:
        """Get font.

        :param str item: font name.
        :returns: FreeTypeFont object.
        """
        if not isinstance(item, str):
            msg = f'Key must be string, got {type(item)}'
            raise KeyError(msg)
        return self.__fonts[item]
