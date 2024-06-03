import datetime
import logging
from pathlib import Path

import click
from PIL import Image

from src.constants import (
    BACKGROUND_COLOR,
    CELL_SIZE,
    FONT,
    MARGINS,
    PLACEHOLDERS_PATH,
)
from src.font_library import FontLibrary
from src.planner import DBDPlanner
from src.renderer import PlanRenderer
from src.types import CoordinatesTuple

TEST_RESULTS_PATH = Path('src/tests/manual_test_results')
logging.basicConfig(format='%(message)s', level=logging.INFO)


@click.group(help='Script for creating images to test generation features.')
def cli() -> None:
    """Group for command line tests."""
    click.echo('Started testing tool of DBDPlanner.')


@cli.command(help='Test creating background image.')
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
    '--cell-size',
    default=CELL_SIZE,
    help=(
        f'Width and height of cell in pixels, default {CELL_SIZE.x} and '
        f'{CELL_SIZE.y}.'
    ),
    type=(int, int),
)
@click.option(
    '--margins',
    default=MARGINS,
    help=(
        f'Two numbers of margins size in pixels: x axis (left and right) and '
        f'y axis (top and bottom). default {MARGINS.x} and {MARGINS.y}.'
    ),
    type=(int, int),
)
@click.option(
    '--color',
    default=BACKGROUND_COLOR,
    help=f'Background color (HTML style), default "{BACKGROUND_COLOR}".',
    type=str,
)
def create_background_image(
    columns: int,
    rows: int,
    cell_size: tuple[int, int],
    margins: tuple[int, int],
    color: str,
) -> None:
    """Test creating background image.

    :param int columns: count columns
    :param int rows: count rows
    :param tuple[int, int] cell_size: width and height of cell
    :param tuple[int, int] margins: margins on x (left and right) and y (top
     and bottom) axes between borders of image and plan.
    :param str color: HTML-style name of background color.
    :return: None
    """
    click.echo('Initializing PlanRenderer...')
    renderer = PlanRenderer(
        dimensions=CoordinatesTuple(x=columns, y=rows),
        cell_size=CoordinatesTuple(x=cell_size[0], y=cell_size[1]),
        margins=CoordinatesTuple(x=margins[0], y=margins[1]),
        background_color=color,
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
def draw_header(columns: int) -> None:
    """Test drawing of plan header.

    :param int columns: count columns
    :return: None
    """
    click.echo('Preparing data...')
    headers = tuple(str(i) for i in range(columns))
    font = FontLibrary()[FONT]
    click.echo('Preparing background...')
    renderer = PlanRenderer(dimensions=CoordinatesTuple(x=columns, y=0))
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
        f'Filename of image from "{PLACEHOLDERS_PATH}" directory that '
        f'need to use as placeholder, default "ash.png". Type "all" to try '
        f'all placeholders.'
    ),
    type=str,
)
def draw_plan(columns: int, rows: int, placeholder: str) -> None:
    """Test drawing plan image by PlanRenderer.

    This test excluding planner logic, that contains calculation like calendar.
    :param int columns: count columns
    :param int rows: count rows
    :param str placeholder: filename of placeholder that will fill all cells.
     Alias "all" available to test on all placeholders in "images" directory.
    :return: None
    """
    if placeholder == 'all':
        placeholders_files = (
            'ash.png',
            'bronze.png',
            'silver.png',
            'gold.png',
            'iridescent.png',
        )
        placeholder_paths = tuple(
            PLACEHOLDERS_PATH / placeholder_file
            for placeholder_file in placeholders_files
        )
    else:
        placeholder_path = PLACEHOLDERS_PATH / placeholder
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
    font = FontLibrary()[FONT]
    click.echo('Preparing background...')
    renderer = PlanRenderer(dimensions=CoordinatesTuple(x=columns, y=rows))
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
    planner = DBDPlanner(date=date, placeholders_path=PLACEHOLDERS_PATH)
    planner.create_plan_image(save_to=TEST_RESULTS_PATH)
