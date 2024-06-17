from collections.abc import Sequence
from pathlib import Path
from typing import Self

from PIL import Image, ImageDraw, ImageOps
from PIL.Image import Resampling
from PIL.ImageFont import FreeTypeFont

from src.constants import PILLOW_MODE, TEXT_ANCHOR
from src.schemas import CustomizationSettings
from src.settings import SETTINGS
from src.types import BoxTuple, CoordinatesTuple, Dimensions, RGBColor, Size


class PlanRenderer:
    """Class that provides to draw image."""

    def __init__(
        self: Self,
        dimensions: Dimensions,
        settings: CustomizationSettings = SETTINGS.customization,
    ) -> None:
        """Initialize background image to render plan on it.

        :param Dimensions dimensions: count of columns (x) and rows (y)
         without header.
        :param Settings settings: pydantic model with settings.
        :returns: None
        """
        self.settings = settings
        self.dimensions = dimensions
        self.placeholder_size: Size = Size(
            width=settings.cell_size.width - settings.cell_paddings.x,
            height=settings.cell_size.height - settings.cell_paddings.y,
        )
        plan_margins = settings.plan_margins
        columns = dimensions.columns
        # plan must contain at least 1 row for header
        rows = dimensions.rows + 1
        image_size = Size(
            width=settings.cell_size.width * columns + plan_margins.x,
            height=settings.cell_size.height * rows + plan_margins.y,
        )
        self.image: Image.Image = Image.new(
            mode=PILLOW_MODE,
            # PyCharm bad works with NamedTuple
            size=image_size,
            color=settings.background_color,
        )
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.image)

    def draw_header(
        self: Self,
        headers: Sequence[str],
        font: FreeTypeFont,
    ) -> None:
        """Draw header like in month calendar: Mon, Tue, Wed etc.

        :param Sequence[str] headers: sequence of text to draw in header. Count
         must be same as count columns that you specified in initialization.
        :param FreeTypeFont font: font of headers.
        :returns: None
        """
        if len(headers) != self.dimensions.columns:
            msg = (
                f'Count headers must be {self.dimensions.columns}, but got '
                f'{len(headers)}'
            )
            raise ValueError(msg)
        plan_margins = self.settings.plan_margins
        for column, text in enumerate(headers):
            top = self.settings.plan_margins.top
            bottom = top + self.settings.cell_size.height
            left = plan_margins.left + self.settings.cell_size.width * column
            right = left + self.settings.cell_size.width
            box = BoxTuple(top=top, right=right, bottom=bottom, left=left)
            self.draw_text_in_box(
                text=text,
                font=font,
                color=self.settings.header_text_color,
                box=box,
            )

    def draw_plan(
        self: Self,
        elements: Sequence[str],
        placeholders: Sequence[Image.Image],
        font: FreeTypeFont,
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
        plan_margins = self.settings.plan_margins
        cell_size = self.settings.cell_size
        cell_paddings = self.settings.cell_paddings
        for element_num, placeholder in enumerate(placeholders):
            column = element_num % self.dimensions.columns
            # first row is header always
            row = (element_num // self.dimensions.columns) + 1
            placeholder_resized = ImageOps.contain(
                image=placeholder,
                # PyCharm bad works with NamedTuple
                size=self.placeholder_size,
                method=Resampling.LANCZOS,
            )
            x_cell = plan_margins.left + column * cell_size.width
            y_cell = plan_margins.top + row * cell_size.height
            # size of placeholder may not exactly equal cell size, so needs to
            #  add insufficient pixels to place placeholder to center of cell
            x_insufficient = cell_size.width - placeholder_resized.size[0]
            y_insufficient = cell_size.height - placeholder_resized.size[1]
            paste_to = CoordinatesTuple(
                x=x_cell + cell_paddings.left + x_insufficient // 2,
                y=y_cell + cell_paddings.top + y_insufficient // 2,
            )
            self.image.paste(
                im=placeholder_resized,
                box=paste_to,
                mask=placeholder_resized,
            )
            top = paste_to.y
            bottom = paste_to.y + placeholder_resized.size[1]
            left = paste_to.x
            right = paste_to.x + placeholder_resized.size[0]
            box = BoxTuple(top=top, right=right, bottom=bottom, left=left)
            self.draw_text_in_box(
                text=elements[element_num],
                font=font,
                color=self.settings.body_text_color,
                box=box,
            )

    def draw_text_in_box(
        self: Self,
        text: str,
        font: FreeTypeFont,
        color: RGBColor | str,
        box: BoxTuple,
    ) -> None:
        """Drawing text in center of box.

        :param str text: text that needs to draw.
        :param FreeTypeFont font: text font.
        :param RGBColor | str color: color of text in HTML word or RGB
         sequence.
        :param BoxTuple box: coordinates of box.
        :return: None
        """
        textbox_dimensions = self.get_textbox_size(text=text, font=font)
        # shift text to draw it at center of box
        x_shift = (box.right - box.left - textbox_dimensions.width) // 2
        y_shift = (box.bottom - box.top - textbox_dimensions.height) // 2
        where_to_draw = CoordinatesTuple(
            x=box.left + x_shift,
            y=box.top + y_shift,
        )
        self.draw.text(
            xy=where_to_draw,
            text=text,
            font=font,
            fill=color,
            anchor=TEXT_ANCHOR,
        )

    def get_textbox_size(
        self: Self,
        text: str,
        font: FreeTypeFont,
    ) -> Size:
        """Get width and height of textbox.

        :param str text: text to get the size from.
        :param FreeTypeFont font: font of text.
        :return: Size object of textbox.
        """
        upper_left_coordinate = CoordinatesTuple(x=0, y=0)
        left, up, width, height = self.draw.textbbox(
            xy=upper_left_coordinate,
            text=text,
            font=font,
            anchor=TEXT_ANCHOR,
        )
        return Size(width=width, height=height)

    def save_image(self: Self, path: Path) -> None:
        """Save plan image.

        :param Path path: where needs to save image.
        :return: None
        """
        self.image.save(path)
