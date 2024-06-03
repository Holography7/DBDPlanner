from collections.abc import Sequence
from typing import Annotated

from pydantic import BaseModel, Field

RGBColorType = Annotated[Sequence[Annotated[int, Field(ge=0, le=255)]], 3]
BoxType = Annotated[Sequence[int], 4] | Annotated[Sequence[int], 2] | int
DimensionsType = Annotated[Sequence[int], 2]


class PathSettings(BaseModel):
    """Scheme of path settings from toml file."""

    fonts: str
    placeholders: str
    plans: str


class CustomizationSettings(BaseModel):
    """Scheme of customization settings from toml file."""

    font: str
    font_size: int
    text_color: RGBColorType | str
    plan_margins: BoxType
    cell_margins: BoxType
    cell_paddings: BoxType
    cell_size: DimensionsType


class TomlSettings(BaseModel):
    """Scheme of settings from toml file."""

    paths: PathSettings
    customization: CustomizationSettings
