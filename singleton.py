from typing import Any, ClassVar, Self


class Singleton(type):
    """Singleton metaclass for stuff that could use lot memory or CPU bound.

    Do not use this metaclass to just make some stuff the single source!
    """

    _instances: ClassVar[dict[Self, Self]] = {}

    # probably not correct typing of return value
    def __call__(cls: Self, *args: Any, **kwargs: Any) -> Self:  # noqa: ANN401
        """Return single instance of class.

        :param Any args: positional arguments for creating class instance.
        :param Any kwargs: keyword arguments for creating class instance.
        :return: class instance.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
