from collections.abc import Sequence
from typing import Self

from pydantic import (
    BaseModel,
    DirectoryPath,
    FilePath,
    PositiveInt,
    field_validator,
    model_validator,
)
from pydantic_core.core_schema import ValidationInfo

from src.enums import StrColor
from src.types import BoxTuple, RGBColor, Size
from src.utils import transform_to_box_tuple


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

    @field_validator('plan_margins', 'cell_paddings', mode='before')
    @classmethod
    def transform_to_box_tuple(
        cls: type[Self],
        raw: int | Sequence[int] | BoxTuple,
    ) -> BoxTuple:
        """Transform raw value to BoxTuple instance.

        :param int | Sequence[int] | BoxTuple raw: integer or sequence with len
         from 1 to 4 that will convert to BoxTuple (tuple with length with 4
         elements).
        :returns: BoxTuple.
        """
        if isinstance(raw, BoxTuple):
            return raw
        return transform_to_box_tuple(value=raw)

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

    @staticmethod
    def __transform_tuple_to_box_tuple(
        raw: Sequence[int],
        info: ValidationInfo,
    ) -> BoxTuple:
        """Transform tuple to BoxTuple instance.

        :param Sequence[int] raw: sequence with len from 1 to 4 that will
         convert to BoxTuple (tuple with length with 4 elements).
        :param ValidationInfo info: pydantic validation info.
        :returns: BoxTuple.
        """
        match len(raw):
            case 1:
                transformed = BoxTuple(
                    top=raw[0],
                    right=raw[0],
                    bottom=raw[0],
                    left=raw[0],
                )
            case 2:
                transformed = BoxTuple(
                    top=raw[0],
                    right=raw[1],
                    bottom=raw[0],
                    left=raw[1],
                )
            case 3:
                transformed = BoxTuple(
                    top=raw[0],
                    right=raw[1],
                    bottom=raw[2],
                    left=raw[1],
                )
            case 4:
                transformed = BoxTuple(
                    top=raw[0],
                    right=raw[1],
                    bottom=raw[2],
                    left=raw[3],
                )
            case _:
                msg = f'{info.field_name} must have length from 1 to 4.'
                raise ValueError(msg)
        return transformed


class Settings(BaseModel):
    """Scheme of settings from toml file."""

    paths: PathSettings
    customization: CustomizationSettings
