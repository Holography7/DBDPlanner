import calendar
import datetime
from pathlib import Path

import numpy as np
from PIL import Image


class DBDPlanner:
    def __init__(self, image_folder: Path = Path('images')):
        self._image_folder = image_folder
        self.months_range = self.count_days = self.months_str = None
        self.year = None

    def select_month(self, year: int, start_month: int):
        """
        :param year: year
        :param start_month: month when starts period. The period is starts on
        13th of start_month and ends 13th of next month, but this planner not
        including 13th day of next month and stops on 12th.
        :return: None
        """
        self.year = year
        self.count_days = calendar.monthrange(year, start_month)[1]
        start_monthcalendar = calendar.monthcalendar(year, start_month)
        if start_month < 12:
            end_month = start_month + 1
            end_year = year
        else:
            end_month = 1
            end_year = year + 1
        end_monthcalendar = calendar.monthcalendar(end_year, end_month)
        # clearing start weeks which not have 13th and replace pre-13th days
        # to None
        while True:
            if 13 in start_monthcalendar[0]:
                weekday_13 = start_monthcalendar[0].index(13)
                for weekday in range(weekday_13):
                    start_monthcalendar[0][weekday] = None
                break
            else:
                start_monthcalendar.pop(0)
        # replace 0 in last week to days of next month
        for i in range(1, start_monthcalendar[-1].count(0) + 1):
            zero = start_monthcalendar[-1].index(0)
            start_monthcalendar[-1][zero] = i
        if 0 in end_monthcalendar[0]:
            end_monthcalendar.pop(0)
        # clearing end weeks which not have 13th and replace post-13th days to
        # None
        while True:
            if 13 in end_monthcalendar[-1]:
                weekday_13 = end_monthcalendar[-1].index(13)
                for weekday in range(weekday_13, 7):
                    end_monthcalendar[-1][weekday] = None
                break
            else:
                end_monthcalendar.pop(-1)
        self.months_range = start_monthcalendar + end_monthcalendar
        start_month_str = datetime.date(year, start_month, 1).strftime('%B')
        end_month_str = datetime.date(end_year, end_month, 1).strftime('%B')
        self.months_str = f'{start_month_str}-{end_month_str}'

    def generate_plan_img(self):
        images = self.months_range.copy()
        for week in range(len(images)):
            for day in range(7):
                if images[week][day] == 4:
                    if self.count_days in (28, 29):
                        images[week][day] = \
                            self._image_folder.joinpath('4_gold.png')
                    else:
                        images[week][day] = \
                            self._image_folder.joinpath('4_iridescent.png')
                elif images[week][day] == 5:
                    if self.count_days == 28:
                        images[week][day] = \
                            self._image_folder.joinpath('5_gold.png')
                    else:
                        images[week][day] = \
                            self._image_folder.joinpath('5_iridescent.png')
                elif images[week][day] is None:
                    continue
                else:
                    images[week][day] = self._image_folder.joinpath(
                        str(images[week][day]),
                    ).with_suffix('.png')
        if len(images) == 5:
            background = np.array(
                Image.open(
                    self._image_folder.joinpath('background_5_weeks.png'),
                ),
            )
        else:
            background = np.array(
                Image.open(
                    self._image_folder.joinpath('background_6_weeks.png'),
                ),
            )
        img_result = background[:, :, :3].copy()
        for line, week in enumerate(images):
            for column, day in enumerate(week):
                if day:
                    img_overlay_rgba = np.array(Image.open(day))
                    img_overlay = img_overlay_rgba[:, :, :3]
                    self.overlay_image_alpha(
                        img_result,
                        img_overlay,
                        50 + 300 * column,
                        300 + 300 * line,
                        img_overlay_rgba[:, :, 3] / 255.0,
                    )
        # Save result
        Image.fromarray(img_result).save(
            f'plans/DBD plan {self.months_str} {self.year}.jpg',
        )
        print(f"Generated plan on {self.months_str} of {self.year}")

    @staticmethod
    def overlay_image_alpha(image, image_overlay, x, y, alpha_mask):
        """
        Overlay `img_overlay` onto `img` at (x, y) and blend using
        `alpha_mask`.

        `alpha_mask` must have same HxW as `img_overlay` and values in range
        [0, 1].
        """
        # Image ranges
        y1, y2 = max(0, y), min(image.shape[0], y + image_overlay.shape[0])
        x1, x2 = max(0, x), min(image.shape[1], x + image_overlay.shape[1])

        # Overlay ranges
        y1o, y2o = max(0, -y), min(image_overlay.shape[0], image.shape[0] - y)
        x1o, x2o = max(0, -x), min(image_overlay.shape[1], image.shape[1] - x)

        # Exit if nothing to do
        if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
            return

        # Blend overlay within the determined ranges
        img_crop = image[y1:y2, x1:x2]
        img_overlay_crop = image_overlay[y1o:y2o, x1o:x2o]
        alpha = alpha_mask[y1o:y2o, x1o:x2o, np.newaxis]
        alpha_inv = 1.0 - alpha

        img_crop[:] = alpha * img_overlay_crop + alpha_inv * img_crop


if __name__ == '__main__':
    planner = DBDPlanner(Path('images'))
    date_today = datetime.date.today()
    year = date_today.year
    month = date_today.month
    if date_today.day < 13:
        month -= 1
    planner.select_month(year=year, start_month=month)
    planner.generate_plan_img()
