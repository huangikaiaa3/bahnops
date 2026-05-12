from psycopg import Connection
from psycopg.rows import dict_row

def get_tracked_targets(connection: Connection) -> list[dict]:
    query = """
        SELECT
            pt.id,
            pt.station_id,
            s.eva_number AS station_eva_number,
            s.name AS station_name,
            pt.target_type,
            pt.poll_interval_seconds,
            pt.is_active
        FROM poll_target pt
        JOIN station s
            ON s.id = pt.station_id
        ORDER BY pt.id;
    """

    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    return rows
