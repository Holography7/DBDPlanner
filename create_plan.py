#!/usr/bin/env python

import datetime
import logging

import click

from src.planner import DBDPlanner

logging.basicConfig(format='%(message)s', level=logging.INFO)


@click.command(
    help=(
        'Create image of plan on selected month for upgrading grades to '
        'Iridescent I. By default it creates plan on current month (between '
        '13th days).'
    ),
)
@click.option(
    '--date',
    '-d',
    default=datetime.date.today(),
    help=(
        'Date in period between 13th days of two months in ISO format '
        '(2024-05-23). For example, if you type date 2024-05-23, script will '
        'create plan between 13th May and 13th June of 2024, but if type '
        '2024-05-12, then it will create between 13th April and 13th May of '
        '2024. Default is today.'
    ),
    type=str,
)
def create_plan(date: datetime.date | str) -> None:
    """Create plan image."""
    planner = DBDPlanner(date=date)
    planner.create_plan_image()


if __name__ == '__main__':
    create_plan()
