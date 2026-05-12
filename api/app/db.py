import psycopg
from api.app.config import config

def get_db_connection():
    with psycopg.connect(config.database_url) as connection:
        yield connection