import calendar
import datetime
import logging
import math
from pathlib import Path
from typing import Self

from PIL import Image

from constants import (
    DAY_WHEN_PERIOD_CHANGES,
    FONT,
    PLACEHOLDERS_PATH,
    PLANS_PATH,
)
from enums import Grade, WeekdayShort
from font_library import FontLibrary
from project_types import AxisTuple
from renderer import PlanRenderer


class DBDPlanner:
    """Class that provides to create plan image."""

    def __init__(
        self: Self,
        year: int,
        month: int,
        placeholders_path: Path = PLACEHOLDERS_PATH,
    ) -> None:
        """Initialize planner object.

        :param int year: year when starts period.
        :param int month: month when starts period.
        :param Path placeholders_path: Path object where stores grades
         placeholders. Default directory is "images" in project directory.
        :return: None
        """
        if not placeholders_path.exists():
            msg = (
                f'Directory with placeholders ({placeholders_path}) does not '
                f'exists'
            )
            raise ValueError(msg)
        self.placeholders_path: Path = placeholders_path
        self.year: int = year
        self.month: int = month
        # monthrange returns tuple with 2 numbers: weekday when month starts
        # and count of days in this month. We took only second
        self.count_days: int = calendar.monthrange(year=year, month=month)[1]

    def create_plan_image(self: Self, save_to: Path = PLANS_PATH) -> None:
        """Create plan image.

        :return: Image
        """
        placeholders_sources: dict[Grade, Image.Image] = {
            grade: Image.open(
                self.placeholders_path / f'{grade.name.lower()}.png',
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
            deadline=self.count_days,
        )
        elements = []
        placeholders = []
        for period_num, days in enumerate(periods):
            grade = Grade(period_num + 1)
            period_placeholder = placeholders_sources[grade]
            for _ in range(days):
                elements.append(str(current_date.day))
                placeholders.append(period_placeholder)
                current_date += datetime.timedelta(days=1)
        columns = len(WeekdayShort)
        rows = math.ceil(len(elements) / columns)
        dimensions = AxisTuple(x=columns, y=rows)
        headers = tuple(weekday.value for weekday in WeekdayShort)
        font = FontLibrary()[FONT]
        renderer = PlanRenderer(dimensions=dimensions)
        renderer.draw_header(headers=headers, font=font)
        renderer.draw_plan(
            elements=elements,
            placeholders=placeholders,
            font=font,
        )
        months_str = f'{current_month_name}-{next_month_name}'
        plan_filename = f'DBD plan {months_str} {self.year}.png'
        renderer.save_image(save_to / plan_filename)
        logging.info('Generated plan on %s of %s.', months_str, self.year)

    @staticmethod
    def calculate_periods(count_periods: int, deadline: int) -> list[int]:
        """Calculate periods in days to upgrade to next grade.

        Each period in this sequence will higher on 1 day of previous, except
        last period that could be higher if left some days before deadline.
        :param int count_periods: count periods
        :param int deadline: count days to upgrade to last grade.
        :return: sequence of count days for each period
        """
        periods = list(range(1, count_periods + 1))
        remain_days = deadline - sum(periods)
        each_period_increment, remain_days = divmod(remain_days, count_periods)
        for period_index in range(len(periods)):
            periods[period_index] += each_period_increment
        periods[-1] += remain_days
        return periods
