import itertools
from collections.abc import Sequence


def product_str(*iterables: Sequence[str]) -> tuple[str, ...]:
    """Join with "," character all cartesian products of string iterables.

    It's shortcut of next code (but with any number of iterables):
    tuple(
        ', '.join(product)
        for product in ((x, y) for x in iterable_1 for y in iterable_2)
    )
    """
    return tuple(
        ', '.join(product) for product in itertools.product(*iterables)
    )
