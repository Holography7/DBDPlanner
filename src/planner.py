import calendar
import datetime
import logging
import math
from typing import Self

from PIL import Image

from src.constants import DAY_WHEN_PERIOD_CHANGES
from src.enums import Grade, WeekdayShort
from src.renderer import PlanRenderer
from src.schemas import Settings
from src.settings import SETTINGS
from src.types import Dimensions


class DBDPlanner:
    """Class that provides to create plan image."""

    def __init__(
        self: Self,
        date: datetime.date | str,
        settings: Settings = SETTINGS,
    ) -> None:
        """Initialize planner object.

        :param datetime.date | str date: date between 13th days of two months.
        :param Settings settings: pydantic model with settings.
        :returns: None
        """
        if isinstance(date, str):
            date_obj = datetime.date.fromisoformat(date)
        else:
            date_obj = date
        if date_obj.day < DAY_WHEN_PERIOD_CHANGES:
            date_obj = date_obj.replace(month=date_obj.month - 1)
        self.settings: Settings = settings
        self.year: int = date_obj.year
        self.month: int = date_obj.month
        # monthrange returns tuple with 2 numbers: weekday when month starts
        # and count of days in this month. We took only second
        self.count_days: int = calendar.monthrange(
            year=self.year,
            month=self.month,
        )[1]

    def create_plan_image(self: Self) -> None:
        """Create plan image.

        :returns: Image
        """
        placeholders_sources: dict[Grade, Image.Image] = {
            grade: Image.open(
                self.settings.paths.placeholders / f'{grade.name.lower()}.png',
            )
            for grade in Grade
        }
        current_date = datetime.date(
            year=self.year,
            month=self.month,
            day=DAY_WHEN_PERIOD_CHANGES,
        )
        end_date = current_date + datetime.timedelta(days=self.count_days)
        current_month_name = current_date.strftime('%B')
        next_month_name = end_date.strftime('%B')
        periods = self.calculate_periods(
            count_periods=len(Grade),
            count_days=self.count_days,
        )
        elements = []
        placeholders = []
        first_day = current_date.weekday()
        for period_num, days in enumerate(periods):
            grade = Grade(period_num + 1)
            period_placeholder = placeholders_sources[grade]
            for _ in range(days):
                elements.append(str(current_date.day))
                placeholders.append(period_placeholder)
                current_date += datetime.timedelta(days=1)
        columns = len(WeekdayShort)
        rows = math.ceil((len(elements) + first_day) / columns)
        dimensions = Dimensions(rows=rows, columns=columns)
        headers = tuple(weekday.value for weekday in WeekdayShort)
        renderer = PlanRenderer(dimensions=dimensions, settings=self.settings)
        renderer.draw_header(headers=headers)
        renderer.draw_plan(
            elements=elements,
            placeholders=placeholders,
            start_from_column=first_day,
        )
        months_str = f'{current_month_name}-{next_month_name}'
        plan_filename = f'DBD plan {months_str} {self.year}.png'
        renderer.save_image(path=self.settings.paths.plans / plan_filename)
        logging.info('Generated plan on %s of %s.', months_str, self.year)

    @staticmethod
    def calculate_periods(count_periods: int, count_days: int) -> list[int]:
        """Calculate periods in days to upgrade to next grade.

        Each period in this sequence will higher on 1 day of previous, except
        last period that could be higher if left some days before deadline.
        :param int count_periods: count periods
        :param int count_days: count days to upgrade to last grade.
        :returns: sequence of count days for each period
        """
        periods = list(range(1, count_periods + 1))
        remain_days = count_days - sum(periods)
        each_period_increment, remain_days = divmod(remain_days, count_periods)
        for period_index in range(len(periods)):
            periods[period_index] += each_period_increment
        periods[-1] += remain_days
        return periods
