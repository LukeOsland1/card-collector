"""MongoDB database configuration and connection management."""
import logging
from typing import AsyncGenerator, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os

from .mongodb_models import (
    Card,
    CardInstance,
    User,
    GuildConfig,
    AuditLog,
    CardSubmission,
)

logger = logging.getLogger(__name__)

# Global MongoDB client
mongodb_client: Optional[AsyncIOMotorClient] = None
database = None


async def init_mongodb(mongodb_url: Optional[str] = None) -> None:
    """Initialize MongoDB connection and Beanie ODM."""
    global mongodb_client, database
    
    if mongodb_url is None:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    database_name = os.getenv("MONGODB_DATABASE", "card_collector")
    
    try:
        # Create MongoDB client
        mongodb_client = AsyncIOMotorClient(mongodb_url)
        database = mongodb_client[database_name]
        
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB at {mongodb_url}")
        
        # Initialize Beanie with document models
        await init_beanie(
            database=database,
            document_models=[
                Card,
                CardInstance,
                User,
                GuildConfig,
                AuditLog,
                CardSubmission,
            ]
        )
        logger.info("Beanie ODM initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb() -> None:
    """Close MongoDB connection."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")


async def get_mongodb_client() -> AsyncIOMotorClient:
    """Get MongoDB client."""
    global mongodb_client
    if mongodb_client is None:
        await init_mongodb()
    return mongodb_client


async def get_database():
    """Get MongoDB database."""
    global database
    if database is None:
        await init_mongodb()
    return database


# Health check function
async def mongodb_health_check() -> dict:
    """Check MongoDB connection health."""
    try:
        client = await get_mongodb_client()
        # Ping the database
        ping_result = await client.admin.command('ping')
        
        # Get database stats
        db = await get_database()
        stats = await db.command("dbStats")
        
        return {
            "status": "healthy",
            "ping": ping_result,
            "database_name": db.name,
            "collections_count": stats.get("collections", 0),
            "data_size": stats.get("dataSize", 0),
            "storage_size": stats.get("storageSize", 0),
        }
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }