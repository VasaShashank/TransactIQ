import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fraud Investigation & Transaction Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkey_change_in_production_environment"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520 # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200 # 30 days

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fraud_db"
    DATABASE_URL: str | None = None

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    REDIS_URL: str = "redis://localhost:6379/0"

    # Risk weights
    WEIGHT_KNOWN_FRAUD: float = 0.35
    WEIGHT_TXN_FREQ: float = 0.20
    WEIGHT_OUTGOING_VOL: float = 0.15
    WEIGHT_NUM_LINKED: float = 0.15
    WEIGHT_CENTRALITY: float = 0.15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
