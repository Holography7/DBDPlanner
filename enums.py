from enum import IntEnum, StrEnum


class Grade(IntEnum):
    ASH = 1
    BRONZE = 2
    SILVER = 3
    GOLD = 4
    IRIDESCENT = 5


class WeekdayShort(StrEnum):
    MONDAY = 'Mon'
    TUESDAY = 'Tue'
    WEDNESDAY = 'Wed'
    THURSDAY = 'Thu'
    FRIDAY = 'Fri'
    SATURDAY = 'Sat'
    SUNDAY = 'Sun'
