from psycopg import Connection
from psycopg.rows import dict_row


def get_station_by_eva_number(eva_number: str, connection: Connection) -> dict | None:
    query = """
        SELECT
            id,
            eva_number,
            name
        FROM station
        WHERE eva_number = %s;
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, (eva_number,))
        row = cursor.fetchone()

    return row


def get_station_services_by_eva_number(eva_number: str, connection: Connection) -> list[dict]:
    query = """
        SELECT
            ssc.service_id,
            se.display_name,
            se.category,
            se.number,
            se.line,
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
        FROM station st
        INNER JOIN poll_target pt
            ON pt.station_id = st.id
        INNER JOIN poll_run pr
            ON pr.poll_target_id = pt.id
        INNER JOIN service_state_current ssc
            ON ssc.latest_poll_run_id = pr.id
        INNER JOIN service_observation so
            ON so.poll_run_id = ssc.latest_poll_run_id
           AND so.service_id = ssc.service_id
        INNER JOIN service se
            ON se.id = ssc.service_id
        WHERE st.eva_number = %s
          AND pt.is_active = TRUE
        ORDER BY
            COALESCE(ssc.current_departure, so.planned_departure, ssc.current_arrival, so.planned_arrival),
            se.display_name,
            ssc.service_id;
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, (eva_number,))
        rows = cursor.fetchall()

    return rows
