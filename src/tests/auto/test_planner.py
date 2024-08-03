from typing import Self

from src.planner import DBDPlanner
from src.types import Dimensions


class TestDBDPlanner:
    """Test planner."""

    def test_calculate_periods(
        self: Self,
        dimensions: Dimensions,
        start_from_column: int,
        count_periods: int,
    ) -> None:
        """Test calculation periods.

        :param Dimensions dimensions: fixture of dimensions of plan.
        :param int start_from_column: fixture with column index where need to
         start draw plan.
        :param int count_periods: fixture with count periods.
        :returns: None
        """
        max_days = dimensions.rows * dimensions.columns
        count_days = max_days - start_from_column
        expected = list(range(1, count_periods + 1))
        used_days = sum(expected)
        days_left = count_days - used_days
        days_increment = days_left // count_periods
        for i in range(count_periods):
            expected[i] += days_increment
        days_left -= days_increment * count_periods
        expected[-1] += days_left

        actual = DBDPlanner.calculate_periods(
            count_periods=count_periods,
            count_days=count_days,
        )

        assert actual == expected
