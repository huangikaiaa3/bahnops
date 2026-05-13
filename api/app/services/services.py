from psycopg import AsyncConnection

from api.app.core.exceptions import ServiceNotFoundError
from api.app.repositories.services import get_service_by_id, get_service_changes_by_id
from api.app.utils.time import db_timetable_to_datetime


async def get_service_detail_response(service_id: int, connection: AsyncConnection) -> dict:
    service_detail = await get_service_by_id(service_id=service_id, connection=connection)

    if service_detail is None:
        raise ServiceNotFoundError

    return build_service_detail_response(service_detail)


async def get_service_changes_response(service_id: int, connection: AsyncConnection) -> list[dict]:
    service = await get_service_by_id(service_id=service_id, connection=connection)

    if service is None:
        raise ServiceNotFoundError

    changes = await get_service_changes_by_id(service_id=service_id, connection=connection)
    return changes


def build_service_detail_response(service_detail: dict) -> dict:
    service_detail["planned_arrival"] = db_timetable_to_datetime(service_detail["planned_arrival"])
    service_detail["current_arrival"] = db_timetable_to_datetime(service_detail["current_arrival"])
    service_detail["planned_departure"] = db_timetable_to_datetime(service_detail["planned_departure"])
    service_detail["current_departure"] = db_timetable_to_datetime(service_detail["current_departure"])

    return service_detail
