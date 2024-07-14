from collections.abc import Sequence

from src.types import BoxTuple


def transform_to_box_tuple(value: int | Sequence[int]) -> BoxTuple:  # noqa: C901
    """Transform integer or tuple to BoxTuple instance.

    :param int | Sequence[int] value: integer or sequence with len from 1 to 4
     that will convert to BoxTuple (tuple with length with 4 elements).
    :returns: BoxTuple.
    """
    if type(value) not in {int, list, tuple}:
        msg = 'Value must be positive integer or list with 1-4 elements'
        raise ValueError(msg)
    if isinstance(value, int):
        return BoxTuple(top=value, right=value, bottom=value, left=value)
    match len(value):
        case 1:
            transformed = BoxTuple(
                top=value[0],
                right=value[0],
                bottom=value[0],
                left=value[0],
            )
        case 2:
            transformed = BoxTuple(
                top=value[0],
                right=value[1],
                bottom=value[0],
                left=value[1],
            )
        case 3:
            transformed = BoxTuple(
                top=value[0],
                right=value[1],
                bottom=value[2],
                left=value[1],
            )
        case 4:
            transformed = BoxTuple(*value)
        case _:
            msg = 'Value must have length from 1 to 4.'
            raise ValueError(msg)
    return transformed
