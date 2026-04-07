from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_user: str = "postgres"
    pg_password: str = "postgres"
    pg_database: str = "ontoagent"

    database_url: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database_url = f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_database}"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
