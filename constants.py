from pathlib import Path

from project_types import AxisTuple

DAY_WHEN_PERIOD_CHANGES = 13
DAYS_OF_FIRST_PERIOD_TO_UPGRADE = 4
PILLOW_MODE = 'RGBA'
BACKGROUND_COLOR = 'black'
FONTS_PATH = Path('fonts')
FONT = "OpenSans-Regular"
FONT_SIZE = 108
TEXT_COLOR = 'white'
TEXT_ANCHOR = 'lt'  # left-top
MARGINS = AxisTuple(x=50, y=0)
PADDINGS = AxisTuple(x=0, y=0)
CELL_SIZE = AxisTuple(x=360, y=360)
PLACEHOLDERS_PATH = Path('images')
PLANS_PATH = Path('plans')
