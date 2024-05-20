from collections.abc import Sequence
from pathlib import Path
from typing import Self

from PIL import Image, ImageDraw, ImageOps
from PIL.Image import Resampling
from PIL.ImageFont import FreeTypeFont

from constants import (
    BACKGROUND_COLOR,
    CELL_SIZE,
    FONT,
    MARGINS,
    PADDINGS,
    PILLOW_MODE,
    TEXT_ANCHOR,
    TEXT_COLOR,
)
from font_library import FONT_LIBRARY
from project_types import AxisTuple


class PlanRenderer:
    """Class that provides to draw image."""

    # actually, there is 5 arguments, exclude self, so ignoring PLR0913 is
    # justified. But don't add any others arguments!
    def __init__(  # noqa: PLR0913
        self: Self,
        dimensions: AxisTuple,
        cell_size: AxisTuple = CELL_SIZE,
        margins: AxisTuple = MARGINS,
        paddings: AxisTuple = PADDINGS,
        background_color: str = BACKGROUND_COLOR,
    ) -> None:
        """Initialize background image to render plan on it.

        :param AxisTuple dimensions: count of columns (x) and rows (y) without
         header.
        :param AxisSize cell_size: width and height of cells. Default:
         (300, 300).
        :param AxisSize margins: two numbers of margins between borders
         of image and plan. First number set margins from left and right,
         second from top and bottom. Default: (50, 0).
        :param str background_color: background color name like in HTML.
         Default: "black".
        :returns: None
        """
        max_x_padding = cell_size.x // 2
        max_y_padding = cell_size.y // 2
        if paddings.x >= max_x_padding or paddings.y >= max_y_padding:
            msg = (
                f'Paddings must be smaller than half of cell, but {paddings} '
                f'>= {(max_x_padding, max_y_padding)}'
            )
            raise ValueError(msg)
        self.dimensions: AxisTuple = dimensions
        self.cell_size: AxisTuple = cell_size
        self.margins: AxisTuple = margins
        self.paddings: AxisTuple = paddings
        self.placeholder_size: AxisTuple = AxisTuple(
            x=cell_size.x - paddings.x * 2,
            y=cell_size.y - paddings.y * 2,
        )
        image_width = cell_size.x * dimensions.x + margins.x * 2
        # plan must contain at least 1 row for header
        rows_with_header = dimensions.y + 1
        image_height = cell_size.y * rows_with_header + margins.y * 2
        image_size = (image_width, image_height)
        self.image: Image.Image = Image.new(
            mode=PILLOW_MODE,
            size=image_size,
            color=background_color,
        )
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.image)

    def draw_header(
        self: Self,
        headers: Sequence[str],
        font: FreeTypeFont = FONT_LIBRARY[FONT],
    ) -> None:
        """Draw header like in month calendar: Mon, Tue, Wed etc.

        :param Sequence[str] headers: sequence of text to draw in header.
        :param FreeTypeFont font: font of headers.
        :returns: None
        """
        y_cell = self.margins.y
        for column, text in enumerate(headers):
            x_cell = self.margins.x + self.cell_size.x * column
            cell_left_top = AxisTuple(x=x_cell, y=y_cell)
            self.draw_text_in_box(
                text=text,
                font=font,
                left_top=cell_left_top,
                box_size=self.cell_size,
            )

    def draw_plan(
        self: Self,
        elements: Sequence[str],
        placeholders: Sequence[Image.Image],
        font: FreeTypeFont = FONT_LIBRARY[FONT],
    ) -> None:
        """Draw plan.

        :param Sequence[str] elements: sequence of text to draw in body of
         plan (numbers of days in months).
        :param Sequence[Image.Image] placeholders: sequence of images that is
         backgrounds for elements.
        :param FreeTypeFont font: font of elements.
        :returns: None
        """
        if len(elements) != len(placeholders):
            msg = 'Sequences of elements and placeholders must have same size.'
            raise ValueError(msg)
        for element_num, placeholder in enumerate(placeholders):
            column = element_num % self.dimensions.x
            row = element_num // self.dimensions.x
            placeholder_resized = ImageOps.contain(
                image=placeholder,
                # PyCharm bad works with NamedTuple
                size=self.placeholder_size,
                method=Resampling.LANCZOS,
            )
            x_cell = self.margins.x + column * self.cell_size.x
            # first row is header always
            y_cell = self.margins.y + (row + 1) * self.cell_size.y
            # size of placeholder may not exactly equal cell size, so needs to
            #  add insufficient pixels to place placeholder to center of cell
            x_insufficient = self.cell_size.x - placeholder_resized.size[0]
            y_insufficient = self.cell_size.y - placeholder_resized.size[1]
            paste_to = AxisTuple(
                x=x_cell + self.paddings.x + x_insufficient // 2,
                y=y_cell + self.paddings.y + y_insufficient // 2,
            )
            self.image.paste(
                im=placeholder_resized,
                box=paste_to,
                mask=placeholder_resized,
            )
            self.draw_text_in_box(
                text=elements[element_num],
                font=font,
                left_top=paste_to,
                box_size=AxisTuple(*placeholder_resized.size),
            )

    def draw_text_in_box(
        self: Self,
        text: str,
        font: FreeTypeFont,
        left_top: AxisTuple,
        box_size: AxisTuple,
    ) -> None:
        """Drawing text in center of box.

        :param str text: text that needs to draw.
        :param FreeTypeFont font: text font.
        :param AxisTuple left_top: left and top coordinate of box.
        :param AxisTuple box_size: size of box.
        :return: None
        """
        textbox_x, textbox_y = self.get_textbox_size(text=text, font=font)
        x_pos = left_top.x + (box_size.x - textbox_x) // 2
        y_pos = left_top.y + (box_size.y - textbox_y) // 2
        self.draw.text(
            xy=(x_pos, y_pos),
            text=text,
            font=font,
            fill=TEXT_COLOR,
            anchor=TEXT_ANCHOR,
        )

    def get_textbox_size(
        self: Self,
        text: str,
        font: FreeTypeFont,
    ) -> tuple[int, int]:
        """Get width and height of textbox.

        :param str text: text to get the size from.
        :param FreeTypeFont font: font of text.
        :return: 2 integer numbers - width and height of textbox.
        """
        upper_left_coordinate = (0, 0)
        left, up, width, height = self.draw.textbbox(
            xy=upper_left_coordinate,
            text=text,
            font=font,
            anchor=TEXT_ANCHOR,
        )
        return width, height

    def save_image(self: Self, path: Path) -> None:
        """Save plan image.

        :param Path path: where needs to save image.
        :return: None
        """
        self.image.save(path)
