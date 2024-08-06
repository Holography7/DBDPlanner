from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Self

from PIL import Image, ImageFont, ImageOps
from PIL.Image import Resampling
from PIL.ImageFont import FreeTypeFont

from src.dataclasses import FontParamsForLoading
from src.settings import SETTINGS
from src.singleton import SingletonABCMeta
from src.types import Size


class BaseMapping(ABC, metaclass=SingletonABCMeta):
    """Base abstract class for all mappings."""

    @abstractmethod
    def __init__(self: Self) -> None:
        """Initialize mapping.

        Please don't use this abstract method and declare your own __init__
        with code below.
        :returns: None
        """
        self.__mapping: dict = {}
        ...

    @abstractmethod
    def add(self: Self, item: Any) -> None:  # noqa: ANN401
        """Add element to mapping.

        :param Any item: any element that need to add to mapping.
        :returns: None
        """
        ...

    @abstractmethod
    def __getitem__(self: Self, key: Any) -> Any:  # noqa: ANN401
        """Get element by item.

        :param Any key: key by which the value is stored.
        :returns: stored value.
        """
        ...

    @abstractmethod
    def __contains__(self: Self, item: Any) -> bool:  # noqa: ANN401
        """Check that item in mapping.

        :param Any item: any element that need to check that exists in mapping.
        :returns: boolean.
        """
        ...

    @abstractmethod
    def clear(self: Self) -> None:
        """Clear mapping.

        Just copy-paste this method to your classes and don't reuse it.
        :returns: None
        """
        self.__mapping = {}


class GetOrAddABCMixin(ABC):
    """Abstract mixin that adding getting or adding element to mapping."""

    @abstractmethod
    def get_or_add(self: Self, item: Any) -> tuple[Any, bool]:  # noqa: ANN401
        """Get or add item to mapping.

        :param Any item: item that need to get ar add to mapping.
        :returns: stored or added value with adding boolean flag.
        """
        ...


class AddOrUpdateMixin(ABC):
    """Abstract mixin that adding or updating element to mapping."""

    @abstractmethod
    def add_or_update(
        self: Self,
        item: Any,  # noqa: ANN401
    ) -> tuple[Any, bool]:
        """Add or update item to mapping.

        :param Any item: item that need to add or update to mapping.
        :returns: added or updated value with adding boolean flag.
        """
        ...


class PlaceholderMapping(BaseMapping, GetOrAddABCMixin):
    """Singleton mapping of IDs original and images of resized placeholders."""

    __resampling_method: ClassVar[Resampling] = (
        SETTINGS.customization.resampling_method
    )
    __resize_to: ClassVar[Size] = (
        SETTINGS.customization.cell_size_without_paddings
    )

    def __init__(self: Self) -> None:
        """Initialize mapping.

        :returns: None
        """
        self.__mapping: dict[int, Image.Image] = {}

    def add(self: Self, item: Image.Image) -> None:
        """Add and resize placeholder to mapping.

        :param Image.Image item: original placeholder image.
        :returns: None
        """
        image_id = id(item)
        if image_id in self.__mapping:
            msg = 'This image already exists in mapping.'
            raise ValueError(msg)
        if item.size == self.__resize_to:
            self.__mapping[image_id] = item
        else:
            self.__mapping[image_id] = ImageOps.contain(
                image=item,
                # PyCharm bad works with NamedTuple
                size=self.__resize_to,
                method=self.__resampling_method,
            )

    def __getitem__(self: Self, key: int) -> Image.Image:
        """Get placeholder.

        :param int key: Image object ID (using id(image)).
        :returns: placeholder resized image.
        """
        if not isinstance(key, int) or key < 0:
            msg = 'Index must be positive integer.'
            raise TypeError(msg)
        return self.__mapping[key]

    def __contains__(self: Self, item: Image.Image) -> bool:
        """Check that placeholder in mapping.

        :param Image.Image item: placeholder that need to check that exists in
         mapping.
        :returns: boolean.
        """
        return id(item) in self.__mapping

    def get_or_add(self: Self, item: Image.Image) -> tuple[Image.Image, bool]:
        """Get or add resized placeholder by original object."""
        image_id = id(item)
        try:
            return self[image_id], False
        except KeyError:
            self.add(item=item)
        return self[image_id], True

    def clear(self: Self) -> None:
        """Clear mapping.

        :returns: None
        """
        self.__mapping = {}


class FontMapping(BaseMapping, AddOrUpdateMixin):
    """Singleton mapping of fonts.

    This mapping have 2 nesting mappings:
     1. Font family names (e.g. OpenSans).
     2. Font style (Bold, Italic, etc.).
     3. Font size.
    """

    def __init__(self: Self) -> None:
        """Initialize mapping.

        :returns: None
        """
        self.__mapping: dict[str, dict[str, dict[float, FreeTypeFont]]] = {}
        self.__path_mapping: dict[Path, dict[float, FreeTypeFont]] = {}

    def add(self: Self, item: FreeTypeFont) -> None:
        """Add font to mapping.

        :param FreeTypeFont item: font object.
        :returns: None
        """
        if not item.font.family or not item.font.style:
            # Real reason unknown, problem detected by mypy
            msg = (
                f'This font have empty family ({item.font.family}) or style '
                f"({item.font.style}). It's dummy?"
            )
            raise ValueError(msg)
        family = item.font.family
        style = item.font.style
        size = item.size
        if family in self.__mapping:
            if style in self.__mapping[family]:
                if size in self.__mapping[family][style]:
                    msg = 'This font already exists in mapping.'
                    raise ValueError(msg)
                self.__mapping[family][style][size] = item
            else:
                self.__mapping[family][style] = {size: item}
        else:
            self.__mapping[family] = {style: {size: item}}

    def __getitem__(
        self: Self,
        key: str,
    ) -> dict[str, dict[float, FreeTypeFont]]:
        """Get style level of mapping.

        This lets you get font next way:
        FontMapping()['OpenSans']['Regular'][108]
        :param str key: font family string.
        :returns: style level mapping.
        """
        if not isinstance(key, str):
            msg = 'Font family must be a string.'
            raise TypeError(msg)
        return self.__mapping[key]

    def __contains__(self: Self, font: FreeTypeFont | Path) -> bool:
        """Check that font exists in mapping.

        :param FreeTypeFont | Path font: font object or path to font.
        :returns: boolean.
        """
        if isinstance(font, Path):
            return font in self.__path_mapping
        family = font.font.family
        style = font.font.style
        size = font.size
        return (
            family in self.__mapping
            and style in self.__mapping[family]
            and size in self.__mapping[family][style]
        )

    def add_or_update(
        self: Self,
        item: FreeTypeFont,
    ) -> tuple[FreeTypeFont, bool]:
        """Add or update font to mapping.

        :param FreeTypeFont item: font that need to add or update to mapping.
        :returns: added or updated font with adding boolean flag.
        """
        if not item.font.family or not item.font.style:
            # Real reason unknown, problem detected by mypy
            msg = (
                f'This font have empty family ({item.font.family}) or style '
                f"({item.font.style}). It's dummy?"
            )
            raise ValueError(msg)
        family = item.font.family
        style = item.font.style
        size = item.size
        font_created = True
        if family in self.__mapping:
            if style in self.__mapping[family]:
                font_created = size not in self.__mapping[family][style]
                self.__mapping[family][style][size] = item
            else:
                self.__mapping[family][style] = {size: item}
        else:
            self.__mapping[family] = {style: {size: item}}
        return item, font_created

    def load(self: Self, font_params: FontParamsForLoading) -> FreeTypeFont:
        """Load font from file and add to mapping.

        Supports only TrueType font
        :param FontParamsForLoading font_params: parameters for loading font.
        :returns: loaded font.
        """
        try:
            return self.__path_mapping[font_params.path][font_params.size]
        except KeyError:
            font = ImageFont.truetype(
                font=font_params.path,
                size=font_params.size,
            )
            if font_params.path in self.__path_mapping:
                self.__path_mapping[font_params.path][font_params.size] = font
            else:
                self.__path_mapping[font_params.path] = {
                    font_params.size: font,
                }
        self.add_or_update(item=font)
        return font

    def clear(self: Self) -> None:
        """Clear mapping.

        :returns: None
        """
        self.__mapping = {}
        self.__path_mapping = {}
