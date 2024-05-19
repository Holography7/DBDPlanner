#!/usr/bin/env python

import datetime
import logging

from constants import DAY_WHEN_PERIOD_CHANGES
from planner import DBDPlanner

if __name__ == '__main__':
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    date_today = datetime.date.today()
    current_year = date_today.year
    current_month = date_today.month
    if date_today.day < DAY_WHEN_PERIOD_CHANGES:
        current_month -= 1
    planner = DBDPlanner(year=current_year, month=current_month)
    planner.create_plan_image()
