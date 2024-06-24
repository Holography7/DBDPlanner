from collections.abc import Sequence
from pathlib import Path
from typing import Literal, Self

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
        self.allowable_placeholder_size: Size = Size(
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
        for element_num, placeholder in enumerate(placeholders):
            column = element_num % self.dimensions.columns
            # first row is header always
            row = (element_num // self.dimensions.columns) + 1
            placeholder_resized = ImageOps.contain(
                image=placeholder,
                # PyCharm bad works with NamedTuple
                size=self.allowable_placeholder_size,
                method=Resampling.LANCZOS,
            )
            paste_to = self.get_coordinate_to_paste_placeholder(
                row=row,
                column=column,
                placeholder_size=Size(*placeholder_resized.size),
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

    def get_coordinate_to_paste_placeholder(
        self: Self,
        row: int,
        column: int,
        placeholder_size: Size,
    ) -> CoordinatesTuple:
        """Get coordinates where need to paste placeholder.

        :param int row: row of plan table.
        :param int column: column of plan table.
        :param Size placeholder_size: placeholder size that need to paste.
        :returns: coordinates where need to paste placeholder.
        """
        self.__validate_dimension(value=row, dimension='Row')
        self.__validate_dimension(value=column, dimension='Column')
        if (
            placeholder_size.width > self.allowable_placeholder_size.width
            or placeholder_size.height > self.allowable_placeholder_size.height
        ):
            msg = (
                f'Placeholder size is out of bounds of free space in cell ('
                f'{placeholder_size} > {self.allowable_placeholder_size})'
            )
            raise ValueError(msg)
        cell_size = self.settings.cell_size
        x_cell = self.settings.plan_margins.left + column * cell_size.width
        y_cell = self.settings.plan_margins.top + row * cell_size.height
        # size of placeholder may not exactly equal cell size, so needs to
        #  add insufficient pixels to place placeholder to center of cell
        x_insufficient = cell_size.width - placeholder_size.width
        y_insufficient = cell_size.height - placeholder_size.height
        return CoordinatesTuple(
            x=x_cell + self.settings.cell_paddings.left + x_insufficient // 2,
            y=y_cell + self.settings.cell_paddings.top + y_insufficient // 2,
        )

    def __validate_dimension(
        self: Self,
        value: int,
        dimension: Literal['Row', 'Column'] = 'Row',
    ) -> None:
        """Validate row or column value.

        :param int value: value.
        :param Literal['Row', 'Column'] dimension: name of dimension, 'Row'
         default.
        :return: None
        """
        if dimension == 'Row':
            max_dimension = self.dimensions.rows
        else:
            max_dimension = self.dimensions.columns
        if value < 0:
            msg = f'{dimension} must be positive integer.'
            raise ValueError(msg)
        if value > max_dimension:
            msg = (
                f'{dimension} is out of bounds for this plan: {value} >= '
                f'{max_dimension}'
            )
            raise ValueError(msg)

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
        textbox_size = self.get_textbox_size(text=text, font=font)
        # shift text to draw it at center of box
        x_shift = (box.right - box.left - textbox_size.width) // 2
        y_shift = (box.bottom - box.top - textbox_size.height) // 2
        where_to_draw = CoordinatesTuple(
            x=box.left + x_shift,
            y=box.top + y_shift,
        )
        where_to_draw = self.get_coordinates_where_draw_text(
            box=box,
            textbox_size=textbox_size,
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

    @staticmethod
    def get_coordinates_where_draw_text(
        box: BoxTuple,
        textbox_size: Size,
    ) -> CoordinatesTuple:
        """Get coordinates where to draw text at center of box.

        :param BoxTuple box: coordinates of box.
        :param AxisTuple textbox_size: size of box with text.
        :return: coordinates where need to draw (CoordinatesTuple)
        text.
        """
        box_size = Size(
            width=box.right - box.left,
            height=box.bottom - box.top,
        )
        if (
            textbox_size.width > box_size.width
            or textbox_size.height > box_size.height
        ):
            msg = (
                f'Textbox is bigger than box where you want draw text. Box '
                f'size: {box_size}, textbox size: {textbox_size}'
            )
            raise ValueError(msg)
        x_shift = (box_size.width - textbox_size.width) // 2
        y_shift = (box_size.height - textbox_size.height) // 2
        return CoordinatesTuple(x=box.left + x_shift, y=box.top + y_shift)

    def save_image(self: Self, path: Path) -> None:
        """Save plan image.

        :param Path path: where needs to save image.
        :return: None
        """
        self.image.save(path)
