import calendar
import datetime
from pathlib import Path

import numpy as np
from PIL import Image

from constants import DAY_WHEN_PERIOD_CHANGES, \
    DAYS_OF_FIRST_PERIOD_TO_UPGRADE, PLACEHOLDERS_PATH, PLANS_PATH
from enums import Grade, WeekdayShort
from renderer import PlanRenderer


class DBDPlanner:
    def __init__(
        self,
        year: int,
        month: int,
        placeholders_path: Path = Path('images'),
    ) -> None:
        """Initialize planner object.
        :param int year: year when starts period.
        :param int month: month when starts period.
        :param Path placeholders_path: Path object where stores grades
         placeholders. Default directory is "images" in project directory.
        :return: None
        """
        if not placeholders_path.exists():
            raise ValueError(
                f"Directory with placeholders ({placeholders_path}) does not "
                f"exists",
            )
        self.placeholders_path: Path = placeholders_path
        self.year: int = year
        self.month: int = month
        # monthrange returns tuple with 2 numbers: weekday when month starts
        # and count of days in this month. We took only second
        self.count_days: int = calendar.monthrange(year=year, month=month)[1]

    def create_plan_image(self) -> None:
        """Create plan image.
        :return: Image
        """
        placeholders_sources: dict[Grade, Image.Image] = {
            grade: Image.open(PLACEHOLDERS_PATH / f'{grade.name.lower()}.png')
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
        # TODO: calculations when need to upgrade grade must be not hardcoded
        #  and be adaptive to different count of grades
        days_left_before_up_grade = DAYS_OF_FIRST_PERIOD_TO_UPGRADE
        days_to_upgrade_increment = 0
        grade = Grade(1)
        elements = []
        placeholders = []
        while current_date < end_date:
            elements.append(str(current_date.day))
            placeholders.append(placeholders_sources[grade])
            current_date += datetime.timedelta(days=1)
            days_left_before_up_grade -= 1
            if days_left_before_up_grade == 0 and grade != Grade.IRIDESCENT:
                days_to_upgrade_increment += 1
                days_left_before_up_grade = (
                    DAYS_OF_FIRST_PERIOD_TO_UPGRADE + days_to_upgrade_increment
                )
                grade = Grade(grade + 1)
        renderer = PlanRenderer(
            headers=WeekdayShort,
            elements=elements,
            placeholders=placeholders,
        )
        renderer.draw_header()
        renderer.draw_plan()
        months_str = f'{current_month_name}-{next_month_name}'
        plan_filename = f'DBD plan {months_str} {self.year}.png'
        renderer.save_image(PLANS_PATH / plan_filename)
        print(f"Generated plan on {months_str} of {self.year}")


if __name__ == '__main__':
    date_today = datetime.date.today()
    year = date_today.year
    month = date_today.month
    if date_today.day < 13:
        month -= 1
    planner = DBDPlanner(year=year, month=month)
    planner.create_plan_image()
