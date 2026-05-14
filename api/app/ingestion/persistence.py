import datetime
import json
from typing import TYPE_CHECKING

from api.app.utils.time import DB_TIMETABLE_TIMEZONE

if TYPE_CHECKING:
    import psycopg


TABLE_CONFIG = {
    "station": {
        "fields": ("eva_number", "name"),
        "on_conflict": {
            "use": True,
            "target": ("eva_number",),
            "action": "DO NOTHING",
        },
    },
    "poll_target": {
        "fields": ("station_id", "target_type", "poll_interval_seconds", "is_active"),
        "on_conflict": {
            "use": True,
            "target": ("station_id", "target_type"),
            "action": "DO UPDATE",
            "set": ("poll_interval_seconds", "is_active"),
        },
    },
    "poll_run": {
        "fields": (
            "poll_target_id",
            "started_at",
            "finished_at",
            "status",
            "services_seen",
            "error_message",
        ),
        "on_conflict": {
            "use": False,
        },
    },
    "service": {
        "fields": ("service_run_uid", "category", "number", "line", "display_name"),
        "on_conflict": {
            "use": True,
            "target": ("service_run_uid",),
            "action": "DO NOTHING",
        },
    },
    "service_observation": {
        "fields": (
            "poll_run_id",
            "service_id",
            "observation_uid",
            "stop_sequence",
            "observed_at",
            "planned_arrival",
            "current_arrival",
            "planned_departure",
            "current_departure",
            "planned_arrival_platform",
            "planned_departure_platform",
            "current_arrival_platform",
            "current_departure_platform",
            "planned_arrival_path",
            "planned_departure_path",
            "current_arrival_path",
            "current_departure_path",
            "raw_snapshot",
        ),
        "on_conflict": {
            "use": True,
            "target": ("poll_run_id", "observation_uid"),
            "action": "DO NOTHING",
        },
    },
    "service_state_current": {
        "fields": (
            "service_id",
            "latest_poll_run_id",
            "last_seen_at",
            "current_arrival",
            "current_departure",
            "current_arrival_platform",
            "current_departure_platform",
            "is_cancelled",
        ),
        "on_conflict": {
            "use": True,
            "target": ("service_id",),
            "action": "DO UPDATE",
            "set": (
                "latest_poll_run_id",
                "last_seen_at",
                "current_arrival",
                "current_departure",
                "current_arrival_platform",
                "current_departure_platform",
                "is_cancelled",
            ),
        },
    },
    "service_state_event": {
        "fields": (
            "service_id",
            "poll_run_id",
            "event_time",
            "event_type",
            "old_value",
            "new_value",
        ),
        "on_conflict": {
            "use": False,
        },
    },
}


def get_station_data(snapshot: dict) -> dict:
    try:
        station_info = snapshot["station"]
    except KeyError as exc:
        raise KeyError("station not found in snapshot") from exc

    return {
        "eva_number": station_info["eva_number"],
        "name": station_info["name"],
    }


def get_id_by_unique_field(table_name: str, lookup_field: str, lookup_value, connection: "psycopg.Connection",) -> int:
    query = f"SELECT id FROM {table_name} WHERE {lookup_field} = %s"

    with connection.cursor() as cursor:
        cursor.execute(query, (lookup_value,))
        row = cursor.fetchone()

    if row is None:
        raise ValueError(
            f"No row found in {table_name} where {lookup_field}={lookup_value!r}"
        )

    return row[0]


def get_poll_target_data(station_id: int) -> dict:
    return {
        "station_id": station_id,
        "target_type": "station_board",
        "poll_interval_seconds": 180,
        "is_active": True,
    }


def get_poll_run_data(
    poll_target_id: int,
    snapshot: dict,
    started_at: datetime.datetime,
    finished_at: datetime.datetime,
) -> dict:
    return {
        "poll_target_id": poll_target_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": "success",
        "services_seen": len(snapshot["services"]),
        "error_message": "",
    }


def get_service_data(snapshot: dict) -> dict[str, dict]:
    service_data = {}
    observed_at = snapshot["captured_at"]

    for service in snapshot["services"]:
        observation_uid = service["service_id"]
        service_run_uid, stop_sequence = observation_uid.rsplit("-", 1)

        service_data[observation_uid] = {
            "service_run_uid": service_run_uid,
            "category": service["category"],
            "number": service["number"],
            "line": service["line"],
            "display_name": service["display_name"],
            "observation_uid": observation_uid,
            "stop_sequence": int(stop_sequence),
            "observed_at": observed_at,
            "planned_arrival": service["planned_arrival"],
            "current_arrival": service["current_arrival"],
            "planned_departure": service["planned_departure"],
            "current_departure": service["current_departure"],
            "planned_arrival_platform": service["planned_arrival_platform"],
            "planned_departure_platform": service["planned_departure_platform"],
            "current_arrival_platform": service["current_arrival_platform"],
            "current_departure_platform": service["current_departure_platform"],
            "planned_arrival_path": json.dumps(service["planned_arrival_path"]),
            "planned_departure_path": json.dumps(service["planned_departure_path"]),
            "current_arrival_path": json.dumps(service["current_arrival_path"]),
            "current_departure_path": json.dumps(service["current_departure_path"]),
            "raw_snapshot": json.dumps(service),
        }

    return service_data


def update_service_data(poll_run_id: int, service_data: dict[str, dict], connection: "psycopg.Connection",) -> dict[str, dict]:
    for observation_uid, observation_data in service_data.items():
        service_run_uid = observation_data["service_run_uid"]
        service_id = get_id_by_unique_field(
            "service",
            "service_run_uid",
            service_run_uid,
            connection,
        )
        service_data[observation_uid]["poll_run_id"] = poll_run_id
        service_data[observation_uid]["service_id"] = service_id

    return service_data


def get_service_state_current_data(service_observation_data: dict[str, dict]) -> dict:
    service_state_current_data = {}

    for observation_uid, observation_data in service_observation_data.items():
        service_state_current_data[observation_uid] = {
            "service_id": observation_data["service_id"],
            "latest_poll_run_id": observation_data["poll_run_id"],
            "last_seen_at": observation_data["observed_at"],
            "current_arrival": observation_data["current_arrival"] or observation_data["planned_arrival"],
            "current_departure": observation_data["current_departure"] or observation_data["planned_departure"],
            "current_arrival_platform": observation_data["current_arrival_platform"] or observation_data["planned_arrival_platform"],
            "current_departure_platform": observation_data["current_departure_platform"] or observation_data["planned_departure_platform"],
            "is_cancelled": False,
        }

    return service_state_current_data


def get_existing_service_state_current(service_id: int, connection: "psycopg.Connection", ) -> dict | None:
    query = """
        SELECT service_id, latest_poll_run_id, last_seen_at, current_arrival, current_departure,
               current_arrival_platform, current_departure_platform, is_cancelled
        FROM service_state_current
        WHERE service_id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (service_id,))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "service_id": row[0],
        "latest_poll_run_id": row[1],
        "last_seen_at": row[2],
        "current_arrival": row[3],
        "current_departure": row[4],
        "current_arrival_platform": row[5],
        "current_departure_platform": row[6],
        "is_cancelled": row[7],
    }


def get_service_state_event_data(service_state_current_data: dict[str, dict], connection: "psycopg.Connection", ) -> list[dict]:
    service_state_event_data = []

    fields_to_compare = {
        "current_arrival": "current_arrival_changed",
        "current_departure": "current_departure_changed",
        "current_arrival_platform": "current_arrival_platform_changed",
        "current_departure_platform": "current_departure_platform_changed",
        "is_cancelled": "is_cancelled_changed",
    }

    for current_state_data in service_state_current_data.values():
        existing_state = get_existing_service_state_current(
            current_state_data["service_id"],
            connection,
        )

        if existing_state is None:
            continue

        for field_name, event_type in fields_to_compare.items():
            old_value = existing_state[field_name]
            new_value = current_state_data[field_name]

            if old_value != new_value:
                service_state_event_data.append(
                    {
                        "service_id": current_state_data["service_id"],
                        "poll_run_id": current_state_data["latest_poll_run_id"],
                        "event_time": current_state_data["last_seen_at"],
                        "event_type": event_type,
                        "old_value": None if old_value is None else str(old_value),
                        "new_value": None if new_value is None else str(new_value),
                    }
                )

    return service_state_event_data


def build_insert_query(target_table: str, return_id: bool = False) -> str:
    table_config = TABLE_CONFIG[target_table]
    columns = table_config["fields"]
    column_list = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    query = f"INSERT INTO {target_table} ({column_list}) VALUES ({placeholders})"

    if table_config["on_conflict"]["use"] and "on_conflict" in table_config:
        conflict = table_config["on_conflict"]
        target = ", ".join(conflict["target"])
        action = conflict["action"]

        if action == "DO NOTHING":
            query += f" ON CONFLICT ({target}) DO NOTHING"
        elif action == "DO UPDATE":
            update_fields = conflict["set"]
            set_clause = ", ".join(
                f"{field} = EXCLUDED.{field}" for field in update_fields
            )
            query += f" ON CONFLICT ({target}) DO UPDATE SET {set_clause}"

    if return_id:
        query += " RETURNING id"

    return query


def build_insert_values(data: dict, target_table: str) -> tuple:
    columns = TABLE_CONFIG[target_table]["fields"]
    return tuple(data[column] for column in columns)


def write_to_table(data: dict, target_table: str, connection: "psycopg.Connection", return_id: bool = False,):
    query = build_insert_query(target_table, return_id=return_id)
    values = build_insert_values(data, target_table)

    with connection.cursor() as cursor:
        cursor.execute(query, values)
        if return_id:
            row = cursor.fetchone()
            return row[0]


def write_snapshot_to_db(database_url: str, snapshot: dict, started_at: datetime.datetime, finished_at: datetime.datetime,) -> None:
    import psycopg

    station_data = get_station_data(snapshot)

    with psycopg.connect(database_url) as connection:
        write_to_table(station_data, "station", connection)

        station_id = get_id_by_unique_field("station", "eva_number", station_data["eva_number"], connection,)
        poll_target_data = get_poll_target_data(station_id)
        write_to_table(poll_target_data, "poll_target", connection)

        poll_target_id = get_id_by_unique_field("poll_target", "station_id", station_id, connection,)
        poll_run_data = get_poll_run_data(
            poll_target_id,
            snapshot,
            started_at,
            finished_at,
        )
        poll_run_id = write_to_table(poll_run_data, "poll_run", connection, return_id=True,)

        service_data = get_service_data(snapshot)
        for service_run_data in service_data.values():
            write_to_table(service_run_data, "service", connection)

        service_observation_data = update_service_data(poll_run_id, service_data, connection, )
        for service_observation in service_observation_data.values():
            write_to_table(service_observation, "service_observation", connection)

        service_state_current_data = get_service_state_current_data(service_observation_data)
        service_state_event_data = get_service_state_event_data(service_state_current_data, connection,)
        
        for current_state_data in service_state_current_data.values():
            write_to_table(current_state_data, "service_state_current", connection)

        for event_data in service_state_event_data:
            write_to_table(event_data, "service_state_event", connection)
