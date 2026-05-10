from __future__ import annotations

import os

import psycopg
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set in .env")

    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("select current_database(), current_user, version()")
            database_name, current_user, version = cursor.fetchone()

    print("PostgreSQL connection successful.")
    print(f"Database: {database_name}")
    print(f"User: {current_user}")
    print(f"Version: {version}")


if __name__ == "__main__":
    main()
