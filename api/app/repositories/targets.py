from psycopg import AsyncConnection
from psycopg.rows import dict_row


async def get_targets(connection: AsyncConnection) -> list[dict]:
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

    async with connection.cursor(row_factory=dict_row) as cursor:
        await cursor.execute(query)
        rows = await cursor.fetchall()

    return rows
