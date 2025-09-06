"""Database abstraction layer supporting both MongoDB and SQL databases."""
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from .config import is_mongodb, get_database_config

logger = logging.getLogger(__name__)

# Import database-specific modules based on configuration
if is_mongodb():
    from .mongodb_base import init_mongodb, close_mongodb, mongodb_health_check
    from .mongodb_crud import (
        MongoCardCRUD as CardCRUD,
        MongoCardInstanceCRUD as CardInstanceCRUD,
        MongoUserCRUD as UserCRUD,
        MongoGuildConfigCRUD as GuildConfigCRUD,
        MongoAuditLogCRUD as AuditLogCRUD,
    )
    from .mongodb_models import (
        Card,
        CardInstance,
        User,
        GuildConfig,
        AuditLog,
        CardSubmission,
        CardRarity,
        CardStatus,
    )
else:
    from .base import get_db, engine, async_engine
    from .crud import (
        CardCRUD,
        CardInstanceCRUD,
        UserCRUD,
        GuildConfigCRUD,
        AuditLogCRUD,
    )
    from .models import (
        Card,
        CardInstance,
        User,
        GuildConfig,
        AuditLog,
        CardSubmission,
        CardRarity,
        CardStatus,
    )


class DatabaseManager:
    """Database manager that abstracts MongoDB and SQL database operations."""
    
    def __init__(self):
        self.is_mongodb = is_mongodb()
        self.config = get_database_config()
    
    async def initialize(self) -> None:
        """Initialize the database connection."""
        if self.is_mongodb:
            mongodb_url = self.config.mongodb_url
            await init_mongodb(mongodb_url)
            logger.info("Initialized MongoDB connection")
        else:
            # SQL database initialization is handled in base.py
            logger.info("Using SQL database connection")
    
    async def close(self) -> None:
        """Close database connections."""
        if self.is_mongodb:
            await close_mongodb()
            logger.info("Closed MongoDB connection")
        else:
            # SQL database cleanup (if needed)
            pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            if self.is_mongodb:
                return await mongodb_health_check()
            else:
                # SQL database health check
                return {
                    "status": "healthy",
                    "database_type": "sql",
                    "database_url": self.config.database_url,
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def migrate_sql_to_mongodb(self) -> Dict[str, Any]:
        """Migrate data from SQL database to MongoDB."""
        if not self.is_mongodb:
            return {"error": "Current database is not MongoDB"}
        
        # This would implement the migration logic
        # For now, return a placeholder
        return {
            "message": "Migration from SQL to MongoDB not yet implemented",
            "status": "pending"
        }


# Global database manager instance
db_manager = DatabaseManager()


async def init_database() -> None:
    """Initialize database connection."""
    await db_manager.initialize()


async def close_database() -> None:
    """Close database connection."""
    await db_manager.close()


async def get_database_health() -> Dict[str, Any]:
    """Get database health status."""
    return await db_manager.health_check()


# Database session/connection getter that works with both systems
async def get_db_session():
    """Get database session (for SQL) or return None (for MongoDB with Beanie)."""
    if is_mongodb():
        # MongoDB uses global connection through Beanie
        return None
    else:
        # SQL database session
        from .base import get_db
        async for session in get_db():
            yield session


# Re-export commonly used items for backward compatibility
__all__ = [
    # Database management
    "db_manager",
    "init_database", 
    "close_database",
    "get_database_health",
    "get_db_session",
    
    # CRUD operations
    "CardCRUD",
    "CardInstanceCRUD", 
    "UserCRUD",
    "GuildConfigCRUD",
    "AuditLogCRUD",
    
    # Models
    "Card",
    "CardInstance",
    "User", 
    "GuildConfig",
    "AuditLog",
    "CardSubmission",
    "CardRarity",
    "CardStatus",
]