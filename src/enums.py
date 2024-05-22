from enum import Enum, IntEnum


class Grade(IntEnum):
    """Enum of grades."""

    ASH = 1
    BRONZE = 2
    SILVER = 3
    GOLD = 4
    IRIDESCENT = 5


class WeekdayShort(Enum):
    """Enum of weekdays, limited 3 letters."""

    MONDAY = 'Mon'
    TUESDAY = 'Tue'
    WEDNESDAY = 'Wed'
    THURSDAY = 'Thu'
    FRIDAY = 'Fri'
    SATURDAY = 'Sat'
    SUNDAY = 'Sun'
