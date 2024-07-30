from collections.abc import Sequence
from pathlib import Path
from typing import LiteralString, Self

from PIL import Image, ImageDraw
from PIL.ImageFont import FreeTypeFont

from src.constants import PILLOW_MODE, TEXT_ANCHOR
from src.dataclasses import FontParams
from src.enums import StrColor
from src.global_mappings import FontMapping, PlaceholderMapping
from src.schemas import Settings
from src.settings import SETTINGS
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
        settings: Settings = SETTINGS,
    ) -> None:
        """Initialize background image to render plan on it.

        :param Dimensions dimensions: count of columns (x) and rows (y)
         without header.
        :param Settings settings: pydantic model with settings.
        :returns: None
        """
        # Initializing attributes
        self.placeholder_mapping = PlaceholderMapping()
        self.font_mapping = FontMapping()
        self.header_font = self.font_mapping.load(
            path=settings.paths.header_font,
            size=settings.customization.header_font_size,
        )
        self.header_text_color = settings.customization.header_text_color
        self.body_font = self.font_mapping.load(
            path=settings.paths.body_font,
            size=settings.customization.body_font_size,
        )
        self.body_text_color = settings.customization.body_text_color
        self.dimensions = dimensions
        self.cell_size = settings.customization.cell_size
        self.plan_margins = settings.customization.plan_margins
        self.cell_paddings = settings.customization.cell_paddings

        # Creating image
        columns = dimensions.columns
        # plan must contain at least 1 row for header
        rows = dimensions.rows + 1
        image_size = Size(
            width=self.cell_size.width * columns + self.plan_margins.x,
            height=self.cell_size.height * rows + self.plan_margins.y,
        )
        self.image: Image.Image = Image.new(
            mode=PILLOW_MODE,
            # PyCharm bad works with NamedTuple
            size=image_size,
            color=settings.customization.background_color,
        )
        self.draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.image)

    def get_font(
        self: Self,
        font: FontParams | FreeTypeFont | None = None,
    ) -> FreeTypeFont:
        """Get font.

        If got FontParams, then try to get font from mapping (could raise
        ValueError if this font not loaded. You should load it manually using
        font_mapping attribute). If got FreeTypeFont, return this font, but add
        it to font_mapping. If got None, then will use header font, loaded from
        settings.
        :param FontParams | FreeTypeFont | None font: font object.
        :returns: font object
        """
        match font:
            case None:
                return self.header_font
            case FreeTypeFont():
                self.font_mapping.add_or_update(item=font)
                return font
            case FontParams():
                family = font.family
                style = font.style
                size = font.size
                try:
                    return self.font_mapping[family][style][size]
                except KeyError as exc:
                    msg = f'Font {family} {style} with size {size} not found'
                    raise ValueError(msg) from exc
            case _:
                msg = f'Unsupported type for getting font: {type(font)}'
                raise TypeError(msg)

    def draw_header(
        self: Self,
        headers: Sequence[str],
        font: FontParams | FreeTypeFont | None = None,
    ) -> None:
        """Draw header like in month calendar: Mon, Tue, Wed etc.

        :param Sequence[str] headers: sequence of text to draw in header. Count
         must be same as count columns that you specified in initialization.
        :param FontParams | FreeTypeFont | None font: font of headers. If got
        FontParams, then try to get font from mapping (could raise ValueError
        if this font not loaded. You should load it manually using font_mapping
        attribute). If got FreeTypeFont, then will use that font directly (
        automatically add this font to font_mapping). If got None, then will
        use header font, loaded from settings.
        :returns: None
        """
        if len(headers) != self.dimensions.columns:
            msg = (
                f'Count headers must be {self.dimensions.columns}, but got '
                f'{len(headers)}'
            )
            raise ValueError(msg)
        font = self.get_font(font=font)
        for column, text in enumerate(headers):
            # first row is header always
            cell = PlanCell(row=0, column=column)
            cell_box = self.get_cell_box(cell=cell)
            self.draw_text_in_box(
                text=text,
                font=font,
                color=self.header_text_color,
                box=cell_box,
            )

    def draw_plan(
        self: Self,
        elements: Sequence[str],
        placeholders: Sequence[Image.Image],
        font: FontParams | FreeTypeFont | None = None,
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
        :param FontParams | FreeTypeFont | None font: font of elements. If got
         FontParams, then try to get font from mapping (could raise ValueError
         if this font not loaded. You should load it manually using
         font_mapping attribute). If got FreeTypeFont, then will use that font
         directly (automatically add this font to font_mapping). If got None,
         then will use body font, loaded from settings.
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
        font = self.get_font(font=font)
        for element_num, placeholder in enumerate(placeholders):
            shifted_element_num = element_num + start_from_column
            cell = PlanCell(
                # first row is header always
                row=(shifted_element_num // columns) + 1,
                column=shifted_element_num % columns,
            )
            cell_box = self.get_cell_box(cell=cell)
            placeholder_resized, _ = self.placeholder_mapping.get_or_add(
                item=placeholder,
            )
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
                color=self.body_text_color,
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
        cell_size = self.cell_size
        plan_margins = self.plan_margins
        cell_paddings = self.cell_paddings
        top_no_padding = plan_margins.top + cell.row * cell_size.height
        left_bo_padding = plan_margins.left + cell.column * cell_size.width
        return BoxTuple(
            top=top_no_padding + cell_paddings.top,
            right=left_bo_padding + cell_size.width - cell_paddings.right,
            bottom=top_no_padding + cell_size.height - cell_paddings.bottom,
            left=left_bo_padding + cell_paddings.left,
        )

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
        color: RGBColor | StrColor,
        box: BoxTuple,
    ) -> None:
        """Drawing text in center of box.

        :param str text: text that needs to draw.
        :param FreeTypeFont font: text font.
        :param RGBColor | StrColor color: color of text in HTML word or RGB
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
