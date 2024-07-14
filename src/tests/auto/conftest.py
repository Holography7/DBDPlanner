import pytest
from _pytest.fixtures import SubRequest

from src.types import BoxTuple, Dimensions, PlanCell, Size
from src.utils import transform_to_box_tuple


@pytest.fixture(
    params=(
        (10, 20, 20, 10),
        (0, 10, 10, 0),
        (10, 100, 100, 10),
        (5, 100, 65, 10),
    ),
)
def box_tuple(request: SubRequest) -> BoxTuple:
    """BoxTuple.

    :param SubRequest request: pytest request with fixture param.
    :returns: BoxTuple object.
    """
    return BoxTuple(*request.param)


@pytest.fixture(params=((10, 10), (50, 50), (70, 30)))
def object_size(request: SubRequest) -> Size:
    """Object size.

    :param SubRequest request: pytest request with fixture param.
    :returns: Size object.
    """
    return Size(*request.param)


@pytest.fixture(
    params=((0, 0), (4, 0), (0, 3), (5, 6)),
    ids=(
        'Row = 0, Column = 0',
        'Row = 4, Column = 0',
        'Row = 0, Column = 3',
        'Row = 5, Column = 6',
    ),
)
def plan_cell(request: SubRequest) -> PlanCell:
    """Plan cell (cell coordinates with row and column).

    :param SubRequest request: pytest request with fixture param.
    :returns: plan cell coordinate.
    """
    return PlanCell(*request.param)


@pytest.fixture(
    params=((3, 2), (5, 3), (6, 6)),
    ids=('Rectangle plan (3x2)', 'Rectangle plan (5x3)', 'Square plan (6x6)'),
)
def dimensions(request: SubRequest) -> Dimensions:
    """Plan dimensions (in rows and columns).

    :param SubRequest request: pytest request with fixture param.
    :returns: Dimensions object.
    """
    return Dimensions(*request.param)


@pytest.fixture(
    params=(
        0,
        (17,),
        (14, 35),
        (42, 15, 65),
        (23, 98, 45, 50),
    ),
    ids=(
        'No margins',
        'All margins with same size',
        'X and Y margins with different size',
        'Only X margins with same size',
        'All margins different',
    ),
)
def plan_margins(request: SubRequest) -> BoxTuple:
    """Plan margins.

    :param SubRequest request: pytest request with fixture param.
    :returns: plan margins.
    """
    return transform_to_box_tuple(value=request.param)


@pytest.fixture(
    params=(
        0,
        (35,),
        (42, 23),
        (89, 12, 31),
        (25, 37, 24, 13),
    ),
    ids=(
        'No paddings',
        'All paddings with same size',
        'X and Y paddings with different size',
        'Only X paddings with same size',
        'All paddings different',
    ),
)
def cell_paddings(request: SubRequest) -> BoxTuple:
    """Cell paddings.

    :param SubRequest request: pytest request with fixture param.
    :returns: cell paddings.
    """
    return transform_to_box_tuple(value=request.param)


@pytest.fixture(
    params=((300, 300), (350, 250), (250, 350)),
    ids=('Square cell', 'Rectangle cell (x > y)', 'Rectangle cell (x < y)'),
)
def cell_size(request: SubRequest) -> Size:
    """Cell size.

    :param SubRequest request: pytest request with fixture param.
    :returns: cell size.
    """
    return Size(*request.param)
