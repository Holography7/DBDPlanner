from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock

import pytest
from _pytest.fixtures import SubRequest
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ImageFont import FreeTypeFont
from pytest_mock import MockFixture

from src.dataclasses import FontParams
from src.global_mappings import FontMapping
from src.schemas import CustomizationSettings, PathSettings, Settings
from src.settings import SETTINGS
from src.types import BoxTuple, Dimensions, PlanCell, Size


@pytest.fixture()
def _mock_textbbox_method(
    mocked_textbox_size: Size,
    mocker: MockFixture,
) -> None:
    """Mock method PIL.ImageDraw.ImageDraw.textbbox.

    :param Size mocked_textbox_size:
    :param MockFixture mocker: fixture of mock module.
    :returns: None
    """
    mocker.patch(
        'PIL.ImageDraw.ImageDraw.textbbox',
        return_value=(0, 0, *mocked_textbox_size),
        spec_set=ImageDraw.ImageDraw.textbbox,
    )


@pytest.fixture()
def _mock_drawing_text(mocker: MockFixture) -> None:
    """Mock method PIL.ImageDraw.ImageDraw.text.

    :param MockFixture mocker: fixture of mock module.
    :returns: None
    """
    mocker.patch(
        'PIL.ImageDraw.ImageDraw.text',
        spec_set=ImageDraw.ImageDraw.text,
    )


@pytest.fixture()
def _mock_font_truetype(mocked_font: Mock, mocker: MockFixture) -> None:
    """Mock method PIL.ImageFont.truetype.

    :param Mock mocked_font: fixture with mocked font.
    :param MockFixture mocker: fixture of mock module.
    :returns: None
    """
    mocker.patch(
        'PIL.ImageFont.truetype',
        return_value=mocked_font,
        spec_set=ImageFont.truetype,
    )


@pytest.fixture()
def _mock_image_contain(
    resized_placeholder: Mock,
    mocker: MockFixture,
) -> None:
    """Mock method PIL.ImageOps.contain.

    :param Mock resized_placeholder: fixture with mocked resized placeholder.
    :param MockFixture mocker: fixture of mock module.
    :returns: None
    """
    mocker.patch(
        'PIL.ImageOps.contain',
        return_value=resized_placeholder,
        spec_set=ImageOps.contain,
    )


@pytest.fixture()
def _mock_image_contain_to_allowable_cell_size(
    resized_placeholder_as_cell: Mock,
    mocker: MockFixture,
) -> None:
    """Mock method PIL.ImageOps.contain by mocked placeholder with cell size.

    :param Mock resized_placeholder_as_cell: fixture with mocked resized
     placeholder that size is equal allowable cell size.
    :param MockFixture mocker: fixture of mock module.
    :returns: None
    """
    mocker.patch(
        'PIL.ImageOps.contain',
        return_value=resized_placeholder_as_cell,
        spec_set=ImageOps.contain,
    )


@pytest.fixture()
def _mock_image_paste(mocker: MockFixture) -> None:
    """Mock method PIL.Image.Image.paste.

    :param MockFixture mocker: fixture of mock module.
    :returns: None
    """
    mocker.patch('PIL.Image.Image.paste', spec_set=Image.Image.paste)


@pytest.fixture(
    params=(
        (9, 9, 9, 9),
        (8, 10, 8, 10),
        (10, 99, 7, 99),
        (11, 56, 65, 10),
    ),
    ids=('(9,9)x(9,9)', '(8,10)x(8,10)', '(10,99)x(7,99)', '(11,56)x(65,10)'),
)
def box_tuple(request: SubRequest) -> BoxTuple:
    """Fixture with BoxTuple.

    :param SubRequest request: pytest request with fixture param.
    :returns: BoxTuple object.
    """
    return BoxTuple(*request.param)


@pytest.fixture(params=((10, 10), (50, 50), (70, 30)))
def object_size(request: SubRequest) -> Size:
    """Fixture with object size.

    :param SubRequest request: pytest request with fixture param.
    :returns: Size object.
    """
    return Size(*request.param)


@pytest.fixture(
    params=((0, 0), (4, 0), (0, 3), (4, 3)),
    ids=(
        'Row = 0, Column = 0',
        'Row = 4, Column = 0',
        'Row = 0, Column = 3',
        'Row = 4, Column = 3',
    ),
)
def plan_cell(request: SubRequest) -> PlanCell:
    """Fixture with plan cell (cell coordinates with row and column).

    :param SubRequest request: pytest request with fixture param.
    :returns: plan cell coordinate.
    """
    return PlanCell(*request.param)


@pytest.fixture(
    params=((6, 9), (8, 5), (6, 6)),
    ids=('Rectangle plan (6x9)', 'Rectangle plan (8x5)', 'Square plan (6x6)'),
)
def dimensions(request: SubRequest) -> Dimensions:
    """Fixture with plan dimensions (in rows and columns).

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
    """Fixture with plan margins.

    :param SubRequest request: pytest request with fixture param.
    :returns: plan margins.
    """
    return BoxTuple.from_int_or_sequence(value=request.param)


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
    """Fixture with cell paddings.

    :param SubRequest request: pytest request with fixture param.
    :returns: cell paddings.
    """
    return BoxTuple.from_int_or_sequence(value=request.param)


@pytest.fixture(
    params=((300, 300), (350, 250), (250, 350)),
    ids=('Square cell', 'Rectangle cell (x > y)', 'Rectangle cell (x < y)'),
)
def cell_size(request: SubRequest) -> Size:
    """Fixture with cell size.

    :param SubRequest request: pytest request with fixture param.
    :returns: cell size.
    """
    return Size(*request.param)


@pytest.fixture()
def mocked_placeholder(mocker: MockFixture) -> Mock:
    """Fixture with mocked placeholder.

    :param MockFixture mocker: fixture of mock module.
    :returns: Mock object with required attributes for tests.
    """
    placeholder = mocker.Mock(spec_set=Image.Image)
    placeholder.size = (300, 300)
    return placeholder  # type: ignore [no-any-return]


@pytest.fixture()
def resized_placeholder(mocker: MockFixture) -> Mock:
    """Fixture with mocked resized placeholder.

    :param MockFixture mocker: fixture of mock module.
    :returns: Mock object with required attributes for tests.
    """
    placeholder = mocker.Mock(spec_set=Image.Image)
    placeholder.size = (130, 130)
    return placeholder  # type: ignore [no-any-return]


@pytest.fixture()
def resized_placeholder_as_cell(
    cell_paddings: BoxTuple,
    cell_size: Size,
    mocker: MockFixture,
) -> Mock:
    """Fixture with mocked resized placeholder with allowable cell size.

    :param BoxTuple cell_paddings: fixture with cell paddings.
    :param Size cell_size: fixture with cell size.
    :param MockFixture mocker: fixture of mock module.
    :returns: Mock object with required attributes for tests.
    """
    placeholder = mocker.Mock(spec_set=Image.Image)
    placeholder.size = (
        cell_size.width - cell_paddings.x,
        cell_size.height - cell_paddings.y,
    )
    return placeholder  # type: ignore [no-any-return]


@pytest.fixture()
def mocked_font(mocker: MockFixture) -> Mock:
    """Fixture with mocked font.

    :param MockFixture mocker: fixture of mock module.
    :returns: Mock object with required attributes for tests.
    """
    font = mocker.Mock(spec=FreeTypeFont)  # spec_set not set "font" attribute
    internal_font = mocker.Mock()  # No spec of internal font
    internal_font.family = 'Test'
    internal_font.style = '1'
    font.font = internal_font
    font.size = 72
    return font  # type: ignore [no-any-return]


@pytest.fixture(params=('family', 'style', 'both'))
def mocked_dummy_font(request: SubRequest, mocker: MockFixture) -> Mock:
    """Fixture with mocked dummy font.

    :param SubRequest request: pytest request with fixture param.
    :param MockFixture mocker: fixture of mock module.
    :returns: Mock object with required attributes for tests.
    """
    font = mocker.Mock(spec=FreeTypeFont)  # spec_set not set "font" attribute
    internal_font = mocker.Mock()  # No spec of internal font
    internal_font.family = 'Test' if request.param == 'style' else None
    internal_font.style = '1' if request.param == 'family' else None
    font.font = internal_font
    font.size = SETTINGS.customization.body_font_size
    return font  # type: ignore [no-any-return]


@pytest.fixture()
def mocked_font_path(mocker: MockFixture) -> Mock:
    """Fixture with mocked path to font.

    :param MockFixture mocker: fixture of mock module.
    :returns: mocked path to font.
    """
    mocked_path = mocker.MagicMock(spec_set=Path)
    mocked_path.exists.return_value = True
    mocked_path.suffix = '.ttf'
    return mocked_path  # type: ignore [no-any-return]


@pytest.fixture(
    params=('font params', 'font object', None),
    ids=('Font params', 'Manually loaded font', 'Default font'),
)
def font_param(
    request: SubRequest,
    mocked_font: Mock,
) -> Generator[FontParams | Mock | None, None, None]:
    """Font parameter for getting font from renderer.

    :param SubRequest request: pytest request with fixture param.
    :param Mock mocked_font: fixture with mocked font.
    :returns: None (default font), FontParams or mocked font object.
    """
    match request.param:
        case None:
            # Use font_size fixture in test to load font with this size as
            # default
            yield None
        case 'font params':
            font_mapping = FontMapping()
            font_mapping.add(item=mocked_font)
            yield FontParams.from_font(font=mocked_font)
            font_mapping.clear()
        case 'font object':
            yield mocked_font
        case _:
            msg = f'Case with parameter {request.param} not implemented'
            raise NotImplementedError(msg)


@pytest.fixture()
def mocked_cell_settings(
    plan_margins: BoxTuple,
    cell_paddings: BoxTuple,
    cell_size: Size,
) -> CustomizationSettings:
    """Fixture with mocked customization settings that changes cell.

    :param BoxTuple plan_margins: fixture with plan margins.
    :param BoxTuple cell_paddings: fixture with cell paddings.
    :param Size cell_size: fixture with cell size.
    :returns: CustomizationSettings with mocked cell_size, paddings and
     margins.
    """
    updated_settings = {
        'plan_margins': plan_margins,
        'cell_paddings': cell_paddings,
        'cell_size': cell_size,
    }
    return SETTINGS.customization.model_copy(update=updated_settings)


@pytest.fixture()
def mocked_path_settings(mocked_font_path: Mock) -> PathSettings:
    """Fixture with path settings with header and body font.

    :param Mock mocked_font_path: fixture with mocked font path.
    :returns: PathSettings with mocked header and body font paths (same at this
     moment).
    """
    updated_settings = {
        'header_font': mocked_font_path,
        'body_font': mocked_font_path,
    }
    return SETTINGS.paths.model_copy(update=updated_settings)


@pytest.fixture()
def mocked_renderer_settings(
    mocked_path_settings: PathSettings,
    mocked_cell_settings: CustomizationSettings,
) -> Settings:
    """Fixture with mocked settings for renderer tests.

    :param PathSettings mocked_path_settings: fixture with mocked path
     settings.
    :param CustomizationSettings mocked_cell_settings: fixture with mocked
     customization settings: plan_margins, cell_paddings and cell_size.
    :returns: settings with mocked font paths, plan margins, cell paddings and
     cell size.
    """
    return SETTINGS.model_copy(
        update={
            'path': mocked_path_settings,
            'customization': mocked_cell_settings,
        },
    )


@pytest.fixture(
    params=((0, 0), (5, 0), (0, 6), (4, 6)),
    ids=(
        'Textbox equal box where need to draw',
        'Textbox width smaller than box where need to draw',
        'Textbox height smaller than box where need to draw',
        'Textbox smaller in both dimensions than box where need to draw',
    ),
)
def mocked_textbox_size(
    request: SubRequest,
    cell_size: Size,
    cell_paddings: BoxTuple,
) -> Size:
    """Fixture with mocked textbox size.

    This fixture must return textbox not bigger than box_tuple fixture to not
    cause errors when trying to get coordinates where place text.
    :param SubRequest request: pytest request with fixture param.
    :param Size cell_size: fixture with cell size.
    :param BoxTuple cell_paddings: fixture with cell paddings.
    :returns: textbox size that will return mocked method.
    """
    width_deductible, height_deductible = request.param
    return Size(
        width=cell_size.width - cell_paddings.x - width_deductible,
        height=cell_size.height - cell_paddings.y - height_deductible,
    )
