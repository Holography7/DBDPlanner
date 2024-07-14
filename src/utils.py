from src.types import BoxTuple


def transform_int_to_box_tuple(value: int) -> BoxTuple:
    """Transform integer to BoxTuple instance.

    :param int value: integer that will convert to BoxTuple (tuple with 4
     elements).
    :returns: BoxTuple.
    """
    if value < 0:
        msg = 'Value must be positive integer'
        raise ValueError(msg)
    return BoxTuple(top=value, right=value, bottom=value, left=value)


def transform_sequence_to_box_tuple(
    value: list[int] | tuple[int, ...],
) -> BoxTuple:
    """Transform list or tuple to BoxTuple instance.

    :param list[int] | tuple[int, ...] value: sequence that will convert to
     BoxTuple (tuple with length 4 elements).
    :returns: BoxTuple.
    """
    match len(value):
        case 1:
            return BoxTuple(
                top=value[0],
                right=value[0],
                bottom=value[0],
                left=value[0],
            )
        case 2:
            return BoxTuple(
                top=value[0],
                right=value[1],
                bottom=value[0],
                left=value[1],
            )
        case 3:
            return BoxTuple(
                top=value[0],
                right=value[1],
                bottom=value[2],
                left=value[1],
            )
        case 4:
            return BoxTuple(*value)
        case _:
            msg = 'Value must be with 1-4 elements.'
            raise ValueError(msg)


def transform_to_box_tuple(
    value: int | list[int] | tuple[int, ...],
) -> BoxTuple:
    """Transform integer or list/tuple to BoxTuple instance.

    :param int | Sequence[int] value: integer or list/tuple with len from 1 to
     4 that will convert to BoxTuple (tuple with 4 elements).
    :returns: BoxTuple.
    """
    if type(value) not in {int, list, tuple}:
        msg = 'Value must be integer or list/tuple with 1-4 elements'
        raise ValueError(msg)
    if isinstance(value, int):
        return transform_int_to_box_tuple(value=value)
    return transform_sequence_to_box_tuple(value=value)
