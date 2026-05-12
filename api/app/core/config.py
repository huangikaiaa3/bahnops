import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL")


config = Config()
