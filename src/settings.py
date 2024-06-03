import tomllib
from pathlib import Path
from typing import Self

from pydantic import ValidationError

from src.constants import SETTINGS_FILE_EXTENSION, SETTINGS_FILE_PATH
from src.dataclasses import Settings
from src.schemas import TomlSettings


class SettingsParser:
    """Class that provides parsing and validation settings file."""

    def __init__(self: Self, settings_file_path: Path) -> None:
        """Import settings from toml file.

        :param Path settings_file_path: Path to toml file with settings.
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
            toml_settings = TomlSettings.model_validate(settings_data)
        except ValidationError as exc:
            custom_error_messages = self.__convert_errors(
                exc=exc,
                custom_messages={},
            )
            raise ValueError(custom_error_messages) from exc
        self.parsed = Settings(toml_data=toml_settings)

    @staticmethod
    def __convert_errors(
        exc: ValidationError,
        custom_messages: dict[str, str],
    ) -> str:
        """Convert pydantic's validation errors to simplified errors for user.

        :param ValidationError exc: pydantic's original exception.
        :param dict[str, str] custom_messages: mapping with custom error
         messages. Default is CUSTOM_VALIDATION_ERROR_MESSAGES constant.
        :returns: Multiline string with simplified validation errors.
        """
        new_errors: list[str] = []
        for error in exc.errors():
            custom_message = custom_messages.get(error['type'])
            if custom_message:
                ctx = error.get('ctx')
                new_error = (
                    custom_message.format(**ctx) if ctx else custom_message
                )
                new_errors.append(new_error)
        return '\n'.join(new_errors)


SETTINGS = SettingsParser(settings_file_path=SETTINGS_FILE_PATH).parsed
