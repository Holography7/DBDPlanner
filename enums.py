from enum import IntEnum, StrEnum


class Grade(IntEnum):
    """Enum of grades."""

    ASH = 1
    BRONZE = 2
    SILVER = 3
    GOLD = 4
    IRIDESCENT = 5


class WeekdayShort(StrEnum):
    """Enum of weekdays, limited 3 letters."""

    MONDAY = 'Mon'
    TUESDAY = 'Tue'
    WEDNESDAY = 'Wed'
    THURSDAY = 'Thu'
    FRIDAY = 'Fri'
    SATURDAY = 'Sat'
    SUNDAY = 'Sun'
