import tomllib
from pathlib import Path
from typing import Self

from pydantic import ValidationError

from src.constants import SETTINGS_FILE_EXTENSION, SETTINGS_FILE_PATH
from src.exceptions import SettingsParsingError
from src.schemas import Settings


class SettingsParser:
    """Class that provides parsing and validation settings file."""

    def __init__(
        self: Self,
        settings_file_path: Path = SETTINGS_FILE_PATH,
    ) -> None:
        """Import settings from toml file.

        :param Path settings_file_path: Path to toml file with settings.
         Default is "settings.toml" in project root.
        :returns: Dataclass with parsed settings.
        """
        if settings_file_path.suffix != SETTINGS_FILE_EXTENSION:
            msg = (
                f'Settings file must be with "{SETTINGS_FILE_EXTENSION}" '
                f'extension.'
            )
            raise ValueError(msg)
        with settings_file_path.open('rb') as settings_file:
            settings_data = tomllib.load(settings_file)
        try:
            self.parsed = Settings.model_validate(settings_data)
        except ValidationError as exc:
            errors = exc.errors()
            raise SettingsParsingError(pydantic_errors=errors) from exc


SETTINGS = SettingsParser(settings_file_path=SETTINGS_FILE_PATH).parsed
