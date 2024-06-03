from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Self

from src.schemas import TomlSettings
from src.types import BoxTuple, Dimensions, RGBColor


@dataclass
class Settings:
    """Dataclass with project settings."""

    toml_data: InitVar[TomlSettings]
    fonts_path: Path = field(init=False)
    placeholders_path: Path = field(init=False)
    plans_path: Path = field(init=False)
    font: Path = field(init=False)
    font_size: int = field(init=False)
    text_color: RGBColor | str = field(init=False)
    plan_margins: BoxTuple = field(init=False)
    cell_margins: BoxTuple = field(init=False)
    cell_paddings: BoxTuple = field(init=False)
    cell_size: Dimensions = field(init=False)

    def __post_init__(self: Self, toml_data: TomlSettings) -> None:
        """Parse data from toml.

        :param dict[str, Any] toml_data: dict with data from toml file.
        :returns: None
        """
        self.fonts_path = Path(toml_data.paths.fonts)
        self.placeholders_path = Path(toml_data.paths.placeholders)
        self.plans_path = Path(toml_data.paths.plans)
        font_file = f'{toml_data.customization.font}.ttf'
        self.font = Path(self.plans_path / font_file)
        self.__check_paths_exists()

    def __check_paths_exists(self: Self) -> None:
        """Check that all paths exists.

        It will raise FileNotFoundError exception if some path does not exist.
        :returns: None
        """
        paths = {
            'Fonts': self.fonts_path,
            'Placeholders': self.placeholders_path,
            'Plans': self.plans_path,
            'Font': self.font,
        }
        for name, path in paths.items():
            if not path.exists():
                msg = f'{name} path "{path}" does not exists.'
                raise FileNotFoundError(msg)
