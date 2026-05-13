from psycopg import AsyncConnection

from api.app.core.exceptions import StationNotFoundError
from api.app.repositories.stations import (
    get_station_by_eva_number,
    get_station_services_by_eva_number,
)
from api.app.utils.time import db_timetable_to_datetime


async def get_station_services_response(eva_number: str, connection: AsyncConnection) -> list[dict]:
    station = await get_station_by_eva_number(eva_number=eva_number, connection=connection)

    if station is None:
        raise StationNotFoundError

    services = await get_station_services_by_eva_number(eva_number=eva_number, connection=connection)
    return build_station_services_response(services)


def build_station_services_response(services: list[dict]) -> list[dict]:
    for service in services:
        service["planned_arrival"] = db_timetable_to_datetime(service["planned_arrival"])
        service["current_arrival"] = db_timetable_to_datetime(service["current_arrival"])
        service["planned_departure"] = db_timetable_to_datetime(service["planned_departure"])
        service["current_departure"] = db_timetable_to_datetime(service["current_departure"])

    return services
