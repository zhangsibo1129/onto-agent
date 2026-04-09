from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from os import getenv
from dotenv import load_dotenv

load_dotenv()


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_user: str = "postgres"
    pg_password: str = "postgres"
    pg_database: str = "ontoagent"

    database_url: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database_url = f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"


@lru_cache
def get_db_settings() -> DatabaseSettings:
    return DatabaseSettings()
