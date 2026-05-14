import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL")
        self.db_client_id = os.getenv("DB_CLIENT_ID")
        self.db_api_key = os.getenv("DB_API_KEY")
        self.db_timetable_base_url = os.getenv("DB_TIMETABLE_BASE_URL")


config = Config()
