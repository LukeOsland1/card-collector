#!/usr/bin/env python3
"""Database initialization script for Card Collector."""
import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from db.base import Base, async_engine, get_database_config
from db.models import *  # noqa: F401,F403

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def check_database_connection():
    """Test database connection."""
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def init_alembic():
    """Initialize Alembic if not already done."""
    if not (project_root / "db" / "migrations" / "versions").exists():
        logger.info("Initializing Alembic...")
        try:
            # Create versions directory
            versions_dir = project_root / "db" / "migrations" / "versions"
            versions_dir.mkdir(parents=True, exist_ok=True)
            
            # Create initial migration
            os.chdir(project_root)
            result = subprocess.run([
                sys.executable, "-m", "alembic", "revision", "--autogenerate", 
                "-m", "Initial migration"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Alembic initialized successfully")
            else:
                logger.error(f"Alembic initialization failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error initializing Alembic: {e}")
            return False
    else:
        logger.info("Alembic already initialized")
    
    return True


def upgrade_database():
    """Run Alembic upgrade."""
    logger.info("Running database migrations...")
    try:
        os.chdir(project_root)
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Database upgraded successfully")
            return True
        else:
            logger.error(f"Database upgrade failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error upgrading database: {e}")
        return False


async def seed_development_data():
    """Add sample data for development."""
    try:
        from db.seeds import seed_development_data as seed_data
        await seed_data()
        logger.info("Development data seeded successfully")
    except ImportError:
        logger.info("ℹ️  No seed data module found, skipping")
    except Exception as e:
        logger.error(f"Error seeding data: {e}")


async def main():
    """Main initialization function."""
    logger.info("Starting database initialization...")
    
    # Get database config
    config = get_database_config()
    logger.info(f"Database URL: {config.database_url}")
    
    # Check connection
    if not await check_database_connection():
        logger.error("Cannot connect to database. Please check your configuration.")
        return False
    
    # Initialize Alembic
    if not init_alembic():
        logger.error("Failed to initialize Alembic")
        return False
    
    # Run migrations
    if not upgrade_database():
        logger.error("Failed to upgrade database")
        return False
    
    # Create tables (fallback if migrations don't work)
    await create_tables()
    
    # Seed development data if requested
    if "--seed" in sys.argv:
        await seed_development_data()
    
    logger.info("Database initialization complete!")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Database initialization cancelled")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)