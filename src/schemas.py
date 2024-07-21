from functools import cached_property
from typing import Self

from PIL.Image import Resampling
from pydantic import (
    BaseModel,
    DirectoryPath,
    FilePath,
    PositiveInt,
    field_validator,
    model_validator,
)

from src.enums import StrColor
from src.types import BoxTuple, RGBColor, Size


class PathSettings(BaseModel):
    """Scheme of path settings from toml file."""

    header_font: FilePath
    body_font: FilePath
    placeholders: DirectoryPath
    plans: DirectoryPath


class CustomizationSettings(BaseModel):
    """Scheme of customization settings from toml file."""

    header_font_size: PositiveInt
    body_font_size: PositiveInt
    header_text_color: RGBColor | StrColor
    body_text_color: RGBColor | StrColor
    background_color: RGBColor | StrColor
    plan_margins: BoxTuple
    cell_paddings: BoxTuple
    cell_size: Size
    resampling_method: Resampling

    @field_validator('resampling_method', mode='before')
    @classmethod
    def transform_to_enum(
        cls: type[Self],
        raw: str | Resampling,
    ) -> Resampling:
        """Transform raw str to Resampling enum.

        :param str | Resampling raw: name of resampling method.
        :returns: one of value of Resampling enum.
        """
        if isinstance(raw, Resampling):
            return raw
        key = raw.upper()
        if key in Resampling.__members__:
            return Resampling.__members__[key]
        msg = f'Resampling method "{raw}" does not exists.'
        raise ValueError(msg)

    @field_validator('plan_margins', 'cell_paddings', mode='before')
    @classmethod
    def transform_to_box_tuple(
        cls: type[Self],
        raw: int | list[int] | tuple[int, ...] | BoxTuple,
    ) -> BoxTuple:
        """Transform raw value to BoxTuple instance.

        :param int | Sequence[int] | BoxTuple raw: integer or sequence with len
         from 1 to 4 that will convert to BoxTuple (tuple with length with 4
         elements).
        :returns: BoxTuple.
        """
        if isinstance(raw, BoxTuple):
            return raw
        return BoxTuple.from_int_or_sequence(value=raw)

    @model_validator(mode='after')
    def check_paddings_not_bigger_than_size(self: Self) -> Self:
        """Check that paddings not bigger that cell size.

        :returns: validated pydantic model.
        """
        max_x_padding = self.cell_size.width // 2
        max_y_padding = self.cell_size.height // 2
        x_padding = self.cell_paddings.right + self.cell_paddings.left
        y_padding = self.cell_paddings.top + self.cell_paddings.bottom
        if x_padding >= max_x_padding or y_padding >= max_y_padding:
            msg = (
                f'Paddings must be smaller than half of cell, but '
                f'{(x_padding, y_padding)} >= {(max_x_padding, max_y_padding)}'
            )
            raise ValueError(msg)
        return self

    @cached_property
    def cell_size_without_paddings(self: Self) -> Size:
        """Get cell size without paddings.

        :returns: cell size without paddings
        """
        return Size(
            width=self.cell_size.width - self.cell_paddings.x,
            height=self.cell_size.height - self.cell_paddings.y,
        )


class Settings(BaseModel):
    """Scheme of settings from toml file."""

    paths: PathSettings
    customization: CustomizationSettings
