"""Database configuration and session management."""
import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool

from .config import get_database_config

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database configuration
db_config = get_database_config()

# Create engines
if db_config.database_url.startswith("sqlite"):
    # SQLite configuration
    # For sync engine, strip async driver from URL
    sync_url = db_config.database_url.replace("sqlite+aiosqlite:", "sqlite:")
    engine = create_engine(
        sync_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=db_config.echo_sql,
    )
    
    # For async engine, ensure proper async URL format
    if "sqlite+aiosqlite:" in db_config.database_url:
        async_url = db_config.database_url  # Already has async driver
    else:
        async_url = db_config.database_url.replace("sqlite:", "sqlite+aiosqlite:")
    
    async_engine = create_async_engine(
        async_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=db_config.echo_sql,
    )
else:
    # PostgreSQL configuration
    engine = create_engine(db_config.database_url, echo=db_config.echo_sql)
    # Convert to async PostgreSQL URL
    async_url = db_config.database_url.replace(
        "postgresql+psycopg://", "postgresql+asyncpg://"
    )
    async_engine = create_async_engine(async_url, echo=db_config.echo_sql)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    """Get synchronous database session for migrations."""
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()