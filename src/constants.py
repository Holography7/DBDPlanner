from pathlib import Path

from src.types import CoordinatesTuple

DAY_WHEN_PERIOD_CHANGES = 13
PILLOW_MODE = 'RGBA'
BACKGROUND_COLOR = 'black'
FONTS_PATH = Path('fonts')
FONT = 'OpenSans-Regular'
FONT_SIZE = 108
TEXT_COLOR = 'white'
TEXT_ANCHOR = 'lt'  # left-top
MARGINS = CoordinatesTuple(x=50, y=0)
PADDINGS = CoordinatesTuple(x=0, y=0)
CELL_SIZE = CoordinatesTuple(x=360, y=360)
PLACEHOLDERS_PATH = Path('images')
PLANS_PATH = Path('plans')
SETTINGS_FILE_EXTENSION = '.toml'
SETTINGS_FILE_PATH = Path('settings.toml')
