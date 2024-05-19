from pathlib import Path

from PIL import Image

from constants import BACKGROUND_COLOR, MARGINS, CELL_SIZE, PLACEHOLDERS_PATH
from enums import WeekdayShort
from project_types import AxisTuple
from renderer import PlanRenderer

try:
    import click
except ImportError:
    raise ImportError(
        'Unable to import module "click". This is a optional dependency, did '
        'you forgot to install it? (Command to install: "pip install '
        'click==8.1.7" or, if you install uv, "uv pip install click==8.1.7")'
    )


TEST_RESULTS_PATH = Path('test_results')


@click.group(help='Script for creating images to test generation features.')
def cli():
    pass


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
    click.echo('Initializing PlanRenderer...')
    headers = tuple(str(i) for i in range(columns))
    elements = tuple(str(i) for i in range(columns * rows))
    placeholder = Image.open(Path('images/ash.png'))
    placeholders = tuple(placeholder for _ in range(columns * rows))
    renderer = PlanRenderer(
        headers=headers,
        elements=elements,
        placeholders=placeholders,
        cell_size=AxisTuple(cell_size[0], cell_size[1]),
        margins=AxisTuple(margins[0], margins[1]),
        background_color=color,
    )
    path = TEST_RESULTS_PATH / "background.png"
    renderer.save_image(path)
    click.echo(f'Image saved in {path}')


@cli.command(help='Test drawing of plan header.')
def draw_header() -> None:
    click.echo('Preparing background...')
    renderer = PlanRenderer(headers=WeekdayShort, elements=(), placeholders=())
    click.echo('Running method "draw_header"...')
    renderer.draw_header()
    path = TEST_RESULTS_PATH / "header.png"
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
        f'Filename of image from "{PLACEHOLDERS_PATH}" directory that need to '
        f'use as placeholder, default "ash.png". Type "all" to try all '
        f'placeholders.'
    ),
    type=str,
)
def draw_plan(columns: int, rows: int, placeholder: str) -> None:
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
            raise ValueError(
                f'Placeholder "{placeholder_path}" does not exists.',
            )
        placeholder_paths = (placeholder_path,)
    click.echo('Preparing data...')
    headers = tuple(str(i) for i in range(columns))
    elements = tuple(str(i) for i in range(columns * rows))
    placeholders_sources = tuple(
        Image.open(placeholder_path) for placeholder_path in placeholder_paths
    )
    placeholders = tuple(
        placeholders_sources[i % len(placeholders_sources)]
        for i in range(columns * rows)
    )
    click.echo('Preparing background...')
    renderer = PlanRenderer(
        headers=headers,
        elements=elements,
        placeholders=placeholders,
    )
    click.echo('Running method "draw_plan"...')
    renderer.draw_plan()
    path = TEST_RESULTS_PATH / "plan.png"
    renderer.save_image(path)
    click.echo(f'Image saved in {path}')


if __name__ == '__main__':
    cli()
