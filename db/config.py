"""Database configuration."""
import os
from typing import Optional, Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    # Database type selection
    database_type: Literal["mongodb", "sqlite", "postgresql"] = Field(
        default="mongodb", 
        description="Database type to use"
    )
    
    # MongoDB settings
    mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL"
    )
    mongodb_database: str = Field(
        default="card_collector",
        description="MongoDB database name"
    )
    
    # SQL database settings (legacy support)
    database_url: str = Field(
        default="sqlite:///dev.db",
        description="SQL database URL for SQLite/PostgreSQL"
    )
    echo_sql: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return DatabaseConfig()


def get_database_type() -> str:
    """Get the configured database type."""
    config = get_database_config()
    return config.database_type


def is_mongodb() -> bool:
    """Check if using MongoDB."""
    return get_database_type() == "mongodb"


def is_sql_database() -> bool:
    """Check if using SQL database (SQLite/PostgreSQL)."""
    return get_database_type() in ["sqlite", "postgresql"]