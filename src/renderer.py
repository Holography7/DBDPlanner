from collections.abc import Sequence
from pathlib import Path
from typing import LiteralString, Self

from PIL import Image, ImageDraw, ImageOps
from PIL.Image import Resampling
from PIL.ImageFont import FreeTypeFont

from src.constants import PILLOW_MODE, TEXT_ANCHOR
from src.schemas import CustomizationSettings
from src.types import (
    BoxTuple,
    CoordinatesTuple,
    Dimensions,
    PlanCell,
    RGBColor,
    Size,
)


class PlanRenderer:
    """Class that provides to draw image."""

    def __init__(
        self: Self,
        dimensions: Dimensions,
        settings: CustomizationSettings,
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
        self.__placeholders_cache: dict[int, Image.Image] = {}

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
        for column, text in enumerate(headers):
            # first row is header always
            cell = PlanCell(row=0, column=column)
            cell_box = self.get_cell_box(cell=cell)
            self.draw_text_in_box(
                text=text,
                font=font,
                color=self.settings.header_text_color,
                box=cell_box,
            )

    def draw_plan(
        self: Self,
        elements: Sequence[str],
        placeholders: Sequence[Image.Image],
        font: FreeTypeFont,
        start_from_column: int = 0,
    ) -> None:
        """Draw plan.

        :param Sequence[str] elements: sequence of text to draw in body of
         plan (numbers of days in months).
        :param Sequence[Image.Image] placeholders: sequence of images that is
         backgrounds for elements. If you use same images in this sequence than
         it's recommend to place in elements of this sequence link to same
         object (not copy entire object or load from disk same image). In
         process of drawing placeholder images could change size (to place into
         cells). The result of changing size will cache in dict where key will
         ID of original object. After caching, every time before change size of
         image, renderer will try to find already resized placeholder to save
         CPU time and reuse it.
        :param FreeTypeFont font: font of elements.
        :param int start_from_column: index of column of first row where need
         to start fill cells by elements and placeholders.
        :returns: None
        """
        if len(elements) != len(placeholders):
            msg = 'Sequences of elements and placeholders must have same size.'
            raise ValueError(msg)
        columns = self.dimensions.columns
        if start_from_column < 0 or start_from_column > columns:
            msg = f'Column index must be between 0 and {columns}.'
            raise ValueError(msg)
        for element_num, placeholder in enumerate(placeholders):
            shifted_element_num = element_num + start_from_column
            cell = PlanCell(
                # first row is header always
                row=(shifted_element_num // columns) + 1,
                column=shifted_element_num % columns,
            )
            placeholder_resized = self.__resize_placeholder(
                placeholder=placeholder,
            )
            cell_box = self.get_cell_box(cell=cell)
            paste_to = self.get_coordinate_to_place_object_at_center(
                box=cell_box,
                object_size=Size(*placeholder_resized.size),
                object_name='Placeholder',
            )
            self.image.paste(
                im=placeholder_resized,
                box=paste_to,
                mask=placeholder_resized,
            )
            placeholder_box = BoxTuple(
                top=paste_to.y,
                right=paste_to.x + placeholder_resized.size[0],
                bottom=paste_to.y + placeholder_resized.size[1],
                left=paste_to.x,
            )
            self.draw_text_in_box(
                text=elements[element_num],
                font=font,
                color=self.settings.body_text_color,
                box=placeholder_box,
            )

    def get_cell_box(self: Self, cell: PlanCell) -> BoxTuple:
        """Get box of cell.

        :param PlanCell cell: cell coordinates (row and column).
        :returns: BoxTuple of cell.
        """
        if (
            cell.row > self.dimensions.rows
            or cell.column > self.dimensions.columns
        ):
            msg = (
                f'Cell coordinate is out of bounds of this plan (row = '
                f'{cell.row}, column = {cell.column}, {self.dimensions})'
            )
            raise ValueError(msg)
        cell_size = self.settings.cell_size
        plan_margins = self.settings.plan_margins
        cell_paddings = self.settings.cell_paddings
        top_no_padding = plan_margins.top + cell.row * cell_size.height
        left_bo_padding = plan_margins.left + cell.column * cell_size.width
        return BoxTuple(
            top=top_no_padding + cell_paddings.top,
            right=left_bo_padding + cell_size.width - cell_paddings.right,
            bottom=top_no_padding + cell_size.height - cell_paddings.bottom,
            left=left_bo_padding + cell_paddings.left,
        )

    def __resize_placeholder(
        self: Self,
        placeholder: Image.Image,
        resampling_method: Resampling = Resampling.LANCZOS,
    ) -> Image.Image:
        """Resize placeholder to place into cell.

        This method using placeholders cache, that stores resized placeholders
        with ID original object as key, so if you try resize Image object that
        was cached, it will not try resize it again and return cached
        placeholder. Also, it will not resize image if it's size is same as
        allowable_placeholder_size.
        :param Image.Image placeholder: placeholder image object.
        :param Resampling resampling_method: Pillow's resampling method.
        :returns: resized placeholder image object.
        """
        image_id = id(placeholder)
        if image_id in self.__placeholders_cache:
            return self.__placeholders_cache[image_id]
        if placeholder.size == self.allowable_placeholder_size:
            self.__placeholders_cache[image_id] = placeholder
            return placeholder
        self.__placeholders_cache[image_id] = ImageOps.contain(
            image=placeholder,
            # PyCharm bad works with NamedTuple
            size=self.allowable_placeholder_size,
            method=resampling_method,
        )
        return self.__placeholders_cache[image_id]

    @staticmethod
    def get_coordinate_to_place_object_at_center(
        box: BoxTuple,
        object_size: Size,
        object_name: LiteralString = 'Object',
    ) -> CoordinatesTuple:
        """Get coordinates where need to paste object at center of box.

        :param BoxTuple box: box where need to place object.
        :param Size object_size: object size that need to paste.
        :param LiteralString object_name: object name as context.
        :returns: coordinates where need to paste object.
        """
        box_size = box.size
        if (
            object_size.width > box_size.width
            or object_size.height > box_size.height
        ):
            msg = (
                f'{object_name.title()} size is out of bounds of box ('
                f'{object_size} > {box_size})'
            )
            raise ValueError(msg)
        # size of object may not exactly equal cell size, so needs to add
        #  insufficient pixels to place placeholder to center of cell
        x_insufficient = (box_size.width - object_size.width) // 2
        y_insufficient = (box_size.height - object_size.height) // 2
        return CoordinatesTuple(
            x=box.left + x_insufficient,
            y=box.top + y_insufficient,
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
        :returns: None
        """
        textbox_size = self.get_textbox_size(text=text, font=font)
        where_to_draw = self.get_coordinate_to_place_object_at_center(
            box=box,
            object_size=textbox_size,
            object_name='Textbox',
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
        :returns: Size object of textbox.
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
        :returns: None
        """
        self.image.save(path)
