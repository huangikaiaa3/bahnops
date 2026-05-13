from datetime import datetime
from zoneinfo import ZoneInfo


DB_TIMETABLE_TIMEZONE = ZoneInfo("Europe/Berlin")


def db_timetable_to_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None

    if len(value) != 10 or not value.isdigit():
        raise ValueError(f"Unsupported DB timetable value: {value!r}")

    year = 2000 + int(value[0:2])
    month = int(value[2:4])
    day = int(value[4:6])
    hour = int(value[6:8])
    minute = int(value[8:10])

    return datetime(year, month, day, hour, minute, tzinfo=DB_TIMETABLE_TIMEZONE)
