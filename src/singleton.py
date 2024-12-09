from abc import ABCMeta
from typing import Any, ClassVar


class SingletonABCMeta(ABCMeta):
    """Singleton abstract metaclass for stuff that could use lot memory or CPU.

    Do not use this metaclass to just make some stuff the single source!
    """

    _instances: ClassVar[dict] = {}

    # probably not correct typing of return value
    def __call__(cls, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """Return single instance of class.

        :param Any args: positional arguments for creating class instance.
        :param Any kwargs: keyword arguments for creating class instance.
        :returns: class instance.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
