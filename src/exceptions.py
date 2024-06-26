from collections.abc import Sequence
from typing import Self

from pydantic_core import ErrorDetails


class SettingsParsingError(Exception):
    """Exception of Parsing settings."""

    def __init__(
        self: Self,
        *args: str,
        pydantic_errors: Sequence[ErrorDetails],
    ) -> None:
        """Convert pydantic errors to custom.

        :param str args: strings of exceptions for custom errors.
        :param Sequence[PydanticError] pydantic_errors: sequence of pydantic
         errors.
        :returns: None
        """
        self.errors: list[str] = [*args]
        for pydantic_error in pydantic_errors:
            loc = '.'.join(map(str, pydantic_error['loc']))
            msg = f'{loc}: {pydantic_error['msg']}'
            self.errors.append(msg)

    def __str__(self: Self) -> str:
        """Return multistring error message.

        :returns: multistring error message.
        """
        return f'Validation errors in settings:\n{'\n'.join(self.errors)}'

    def __repr__(self: Self) -> str:
        """Return multistring error message.

        :returns: multistring error message.
        """
        return f'Validation errors in settings:\n{'\n'.join(self.errors)}'
