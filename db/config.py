"""Database configuration."""
import os
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    database_url: str = "sqlite:///dev.db"
    echo_sql: bool = False

    class Config:
        env_file = ".env"


def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return DatabaseConfig()