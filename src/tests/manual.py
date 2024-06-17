import datetime
import logging
from pathlib import Path
from typing import Any

import click
from PIL import Image

from src.font_library import FontLibrary
from src.planner import DBDPlanner
from src.renderer import PlanRenderer
from src.settings import SETTINGS
from src.types import BoxTuple, Dimensions, RGBColor, Size

TEST_RESULTS_PATH = Path('src/tests/manual_test_results')
logging.basicConfig(format='%(message)s', level=logging.INFO)


@click.group(help='Script for creating images to test generation features.')
def cli() -> None:
    """Group for command line tests."""
    click.echo('Started testing tool of DBDPlanner.')


@cli.command(help='Test creating background image.')
@click.option(
    '--dimensions',
    default=(1, 1),
    help='Count of rows (without header) and columns, default 1 1.',
    type=(int, int),
)
@click.option(
    '--cell-size',
    help=(
        'Width and height of cell in pixels, default is value, selected in '
        'settings.toml.'
    ),
    type=(int, int),
)
@click.option(
    '--margins',
    help=(
        'Four numbers of margins size in pixels between borders of image and '
        'plan: top, right, bottom and left. Default is value, selected in '
        'settings.toml.'
    ),
    type=(int, int, int, int),
)
@click.option(
    '--html-color',
    help=(
        'Background color in HTML style. Default is value, selected in '
        'settings.toml.'
    ),
    type=str,
)
@click.option(
    '--rgb-color',
    help=(
        'Background color in 3 RGB numbers. Default is value, selected in '
        'settings.toml.'
    ),
    type=(int, int, int),
)
def create_background_image(
    dimensions: tuple[int, int],
    cell_size: tuple[int, int] | None,
    margins: tuple[int, int, int, int] | None,
    html_color: str | None,
    rgb_color: tuple[int, int, int] | None,
) -> None:
    """Test creating background image.

    :param tuple[int, int] dimensions: count rows (without header) and columns
    :param tuple[int, int] | None cell_size: width and height of cell
    :param tuple[int, int, int, int] | None margins: margins between borders of
     image and plan: top, right, bottom and left.
    :param str | tuple[int, int, int] | None html_color: HTML-style name of
     background color.
    :param tuple[int, int, int] | None rgb_color: 3 RGB numbers of background
     color. Overrides --hrml-color if selected.
    :return: None
    """
    updated_settings: dict[str, Any] = {}
    if cell_size:
        updated_settings['cell_size'] = Size(*cell_size)
    if margins:
        updated_settings['plan_margins'] = BoxTuple(*margins)
    if html_color:
        updated_settings['background_color'] = html_color
    if rgb_color:
        updated_settings['background_color'] = RGBColor(*rgb_color)
    overridden_settings = SETTINGS.customization.model_copy(
        update=updated_settings,
    )
    click.echo('Initializing PlanRenderer...')
    renderer = PlanRenderer(
        dimensions=Dimensions(*dimensions),
        settings=overridden_settings,
    )
    path = TEST_RESULTS_PATH / 'background.png'
    renderer.save_image(path)
    click.echo(f'Image saved in {path}')


@cli.command(help='Test drawing of plan header.')
@click.option(
    '--columns',
    default=1,
    help='Count of columns, default 1.',
    type=int,
)
@click.option(
    '--html-color',
    help=(
        'Text color in HTML style. Default is value, selected in '
        'settings.toml.'
    ),
    type=str,
)
@click.option(
    '--rgb-color',
    help=(
        'Text color in 3 RGB numbers. Default is value, selected in '
        'settings.toml.'
    ),
    type=(int, int, int),
)
def draw_header(
    columns: int,
    html_color: str | None,
    rgb_color: tuple[int, int, int] | None,
) -> None:
    """Test drawing of plan header.

    :param int columns: count columns
    :param str | tuple[int, int, int] | None html_color: HTML-style name of
     text color.
    :param tuple[int, int, int] | None rgb_color: 3 RGB numbers of text color.
     Overrides --hrml-color if selected.
    :return: None
    """
    updated_settings: dict[str, Any] = {}
    if html_color:
        updated_settings['header_text_color'] = html_color
    if rgb_color:
        updated_settings['header_text_color'] = RGBColor(*rgb_color)
    overridden_settings = SETTINGS.customization.model_copy(
        update=updated_settings,
    )
    click.echo('Preparing data...')
    headers = tuple(str(i) for i in range(columns))
    font = FontLibrary()[SETTINGS.paths.header_font.stem]
    click.echo('Preparing background...')
    renderer = PlanRenderer(
        dimensions=Dimensions(columns=columns, rows=0),
        settings=overridden_settings,
    )
    click.echo('Running method "draw_header"...')
    renderer.draw_header(headers=headers, font=font)
    path = TEST_RESULTS_PATH / 'header.png'
    renderer.save_image(path)
    click.echo(f'Image saved in {path}')


@cli.command(help='Test drawing plan without header.')
@click.option(
    '--columns',
    default=1,
    help='Count of columns, default 1.',
    type=int,
)
@click.option(
    '--rows',
    default=1,
    help='Count of rows without header, default 1',
    type=int,
)
@click.option(
    '--placeholder',
    default='ash.png',
    help=(
        'Filename of image that need to use as placeholder from setting '
        '"paths.placeholders", default "ash.png". Type "all" to try all '
        'placeholders.'
    ),
    type=str,
)
@click.option(
    '--html-color',
    help=(
        'Text color in HTML style. Default is value, selected in '
        'settings.toml.'
    ),
    type=str,
)
@click.option(
    '--rgb-color',
    help=(
        'Text color in 3 RGB numbers. Default is value, selected in '
        'settings.toml.'
    ),
    type=(int, int, int),
)
def draw_plan(
    columns: int,
    rows: int,
    placeholder: str,
    html_color: str | None,
    rgb_color: tuple[int, int, int] | None,
) -> None:
    """Test drawing plan image by PlanRenderer.

    This test excluding planner logic, that contains calculation like calendar.
    :param int columns: count columns
    :param int rows: count rows
    :param str placeholder: filename of placeholder that will fill all cells.
     Alias "all" available to test on all placeholders in "images" directory.
    :param str | tuple[int, int, int] | None html_color: HTML-style name of
     text color.
    :param tuple[int, int, int] | None rgb_color: 3 RGB numbers of text color.
     Overrides --hrml-color if selected.
    :return: None
    """
    updated_settings: dict[str, Any] = {}
    if html_color:
        updated_settings['body_text_color'] = html_color
    if rgb_color:
        updated_settings['body_text_color'] = RGBColor(*rgb_color)
    overridden_settings = SETTINGS.customization.model_copy(
        update=updated_settings,
    )
    if placeholder == 'all':
        placeholders_files = (
            'ash.png',
            'bronze.png',
            'silver.png',
            'gold.png',
            'iridescent.png',
        )
        placeholder_paths = tuple(
            SETTINGS.paths.placeholders / placeholder_file
            for placeholder_file in placeholders_files
        )
    else:
        placeholder_path = SETTINGS.paths.placeholders / placeholder
        if not placeholder_path.exists():
            msg = f'Placeholder "{placeholder_path}" does not exists.'
            raise FileNotFoundError(msg)
        placeholder_paths = (placeholder_path,)
    click.echo('Preparing data...')
    elements = tuple(str(i) for i in range(columns * rows))
    placeholders_sources = tuple(
        Image.open(placeholder_path) for placeholder_path in placeholder_paths
    )
    placeholders = tuple(
        placeholders_sources[i % len(placeholders_sources)]
        for i in range(columns * rows)
    )
    font = FontLibrary()[SETTINGS.paths.body_font.stem]
    click.echo('Preparing background...')
    renderer = PlanRenderer(
        dimensions=Dimensions(columns=columns, rows=rows),
        settings=overridden_settings,
    )
    click.echo('Running method "draw_plan"...')
    renderer.draw_plan(elements=elements, placeholders=placeholders, font=font)
    path = TEST_RESULTS_PATH / 'plan.png'
    renderer.save_image(path)
    click.echo(f'Image saved in {path}')


@cli.command(help='Test creating plan.')
@click.option(
    '--date',
    '-d',
    default=datetime.date.today(),
    help=(
        'Date in period between 13th days of two months in ISO format '
        '(2024-05-23). For example, if you type date 2024-05-23, script will '
        'create plan between 13th May and 13th June of 2024, but if type '
        '2024-05-12, then it will create between 13th April and 13th May of '
        '2024. Default is today.'
    ),
    type=str,
)
def create_plan(date: datetime.date | str) -> None:
    """Test creating plan.

    This test contains calendar logic, so it's closest to testing all features.
    :return: None
    """
    overridden_settings = SETTINGS.model_copy(
        update={'paths.plans': TEST_RESULTS_PATH},
    )
    planner = DBDPlanner(date=date, settings=overridden_settings)
    planner.create_plan_image()
