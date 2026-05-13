from psycopg import Connection
from psycopg.rows import dict_row


def get_service_by_id(service_id: int, connection: Connection) -> dict | None:
    query = """
        SELECT
            s.id AS service_id,
            s.service_run_uid,
            s.display_name,
            s.category,
            s.number,
            s.line,
            so.planned_arrival,
            ssc.current_arrival,
            so.planned_departure,
            ssc.current_departure,
            so.planned_arrival_platform,
            ssc.current_arrival_platform,
            so.planned_departure_platform,
            ssc.current_departure_platform,
            ssc.is_cancelled,
            ssc.last_seen_at
        FROM service s
        INNER JOIN service_state_current ssc
            ON ssc.service_id = s.id
        INNER JOIN service_observation so
            ON so.poll_run_id = ssc.latest_poll_run_id
           AND so.service_id = ssc.service_id
        WHERE s.id = %s;
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, (service_id,))
        row = cursor.fetchone()

    return row


def get_service_changes_by_id(service_id: int, connection: Connection) -> list[dict]:
    query = """
        SELECT
            service_id,
            poll_run_id,
            event_time,
            event_type,
            old_value,
            new_value
        FROM service_state_event
        WHERE service_id = %s
        ORDER BY event_time ASC, id ASC;
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, (service_id,))
        rows = cursor.fetchall()

    return rows
