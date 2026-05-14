from datetime import datetime, timedelta
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

def get_fetch_plan_target_time(time_now: datetime, hour_offset: int) -> tuple[str, str]:
    target_datetime = time_now - timedelta(hours=hour_offset)
    target_date = str(target_datetime.year)[2:] + str(target_datetime.month).zfill(2) + str(target_datetime.day).zfill(2)
    target_hour = str(target_datetime.hour).zfill(2)
    return target_date, target_hour
