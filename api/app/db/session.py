from psycopg import AsyncConnection

from api.app.core.config import config


async def get_db_connection():
    async with await AsyncConnection.connect(config.database_url) as connection:
        yield connection
