from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Self

from PIL import Image, ImageFont, ImageOps
from PIL.Image import Resampling
from PIL.ImageFont import FreeTypeFont

from src.constants import FONT_EXTENSION
from src.settings import SETTINGS
from src.singleton import SingletonABCMeta
from src.types import Size


class BaseMapping(ABC, metaclass=SingletonABCMeta):
    """Base abstract class for all mappings."""

    @property
    @abstractmethod
    def _mapping(self: Self) -> dict:
        """Mapping.

        :returns: mapping as dictionary.
        """
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

        :param Hashable key: key by which the value is stored.
        :returns: stored value.
        """
        ...

    @classmethod
    def clear(cls: type[Self]) -> None:
        """Clear mapping.

        :returns: None
        """
        cls._mapping = {}  # type: ignore [method-assign, assignment]


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

    _mapping: ClassVar[dict[int, Image.Image]] = {}
    __resampling_method: ClassVar[Resampling] = (
        SETTINGS.customization.resampling_method
    )
    __resize_to: ClassVar[Size] = (
        SETTINGS.customization.cell_size_without_paddings
    )

    def add(self: Self, item: Image.Image) -> None:
        """Add and resize placeholder to mapping.

        :param Image.Image item: original placeholder image.
        :returns: None
        """
        image_id = id(item)
        if image_id in self._mapping:
            msg = 'This image already exists in mapping.'
            raise ValueError(msg)
        if item.size == self.__resize_to:
            self._mapping[image_id] = item
        else:
            self._mapping[image_id] = ImageOps.contain(
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
        return self._mapping[key]

    def get_or_add(self: Self, item: Image.Image) -> tuple[Image.Image, bool]:
        """Get or add resized placeholder by original object."""
        image_id = id(item)
        try:
            return self[image_id], False
        except KeyError:
            self.add(item=item)
        return self[image_id], True


class FontMapping(BaseMapping, AddOrUpdateMixin):
    """Singleton mapping of fonts.

    This mapping have 2 nesting mappings:
     1. Font family names (e.g. OpenSans).
     2. Font style (Bold, Italic, etc.).
     3. Font size.
    """

    _mapping: ClassVar[dict[str, dict[str, dict[float, FreeTypeFont]]]] = {}
    __path_mapping: ClassVar[dict[Path, dict[int, FreeTypeFont]]] = {}

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
        if family in self._mapping:
            if style in self._mapping[family]:
                if size in self._mapping[family][style]:
                    msg = 'This font already exists in mapping.'
                    raise ValueError(msg)
                self._mapping[family][style][size] = item
            else:
                self._mapping[family][style] = {size: item}
        else:
            self._mapping[family] = {style: {size: item}}

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
        return self._mapping[key]

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
        font_exists = False
        if family in self._mapping:
            if style in self._mapping[family]:
                font_exists = size in self._mapping[family][style]
                self._mapping[family][style][size] = item
            else:
                self._mapping[family][style] = {size: item}
        else:
            self._mapping[family] = {style: {size: item}}
        return item, font_exists

    def is_font_exists(self: Self, font: FreeTypeFont) -> bool:
        """Check that font exists in mapping.

        :param FreeTypeFont font: font object.
        :returns: boolean.
        """
        family = font.font.family
        style = font.font.style
        size = font.size
        return (
            family in self._mapping
            and style in self._mapping[family]
            and size in self._mapping[family][style]
        )

    def load(self: Self, path: Path, size: int) -> FreeTypeFont:
        """Load font from file and add to mapping.

        :param Path path: path to font file (TrueType only).
        :param int size: font size.
        :returns: loaded font.
        """
        if not path.exists():
            msg = f'Font not found: {path}'
            raise FileNotFoundError(msg)
        if path.suffix != FONT_EXTENSION:
            msg = f'Only "{FONT_EXTENSION}" allowed, got {path.suffix}'
            raise ValueError(msg)
        try:
            return self.__path_mapping[path][size]
        except KeyError:
            font = ImageFont.truetype(font=path, size=size)
            if path in self.__path_mapping:
                self.__path_mapping[path][size] = font
            else:
                self.__path_mapping[path] = {size: font}
        self.add_or_update(item=font)
        return font

    @classmethod
    def clear(cls: type[Self]) -> None:
        """Clear mapping.

        :returns: None
        """
        super().clear()
        cls.__path_mapping = {}
