import tomllib
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.constants import SETTINGS_FILE_PATH
from src.exceptions import SettingsParsingError
from src.schemas import Settings


class SettingsParser:
    """Class that provides parsing and validation settings file."""

    @staticmethod
    def parse_toml(path: Path = SETTINGS_FILE_PATH) -> dict[str, Any]:
        """Parse toml file.

        :param Path path: path to toml file.
        :returns: dict of parsed file.
        """
        if path.suffix != SETTINGS_FILE_PATH.suffix:
            msg = (
                f'Settings file must be with "{SETTINGS_FILE_PATH.suffix}" '
                f'extension.'
            )
            raise ValueError(msg)
        with path.open('rb') as settings_file:
            return tomllib.load(settings_file)

    @staticmethod
    def parse_data(data: dict[str, Any]) -> Settings:
        """Parse settings from dict.

        :param dict[str, Any] data: dict with settings.
        :returns: Settings pydantic model with parsed settings.
        """
        try:
            settings: Settings = Settings.model_validate(obj=data)
        except ValidationError as exc:
            errors = exc.errors()
            raise SettingsParsingError(pydantic_errors=errors) from exc
        return settings

    @staticmethod
    def load_settings_from_toml(path: Path = SETTINGS_FILE_PATH) -> Settings:
        """Load settings from toml file.

        :param Path path: path to toml file.
        :returns: Settings pydantic model with parsed settings.
        """
        parsed_toml = SettingsParser.parse_toml(path=path)
        return SettingsParser.parse_data(parsed_toml)
