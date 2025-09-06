"""MongoDB database configuration and connection management."""
import logging
import os
from datetime import datetime
from typing import AsyncGenerator, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

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


async def create_collections_explicitly() -> None:
    """Explicitly create collections if Beanie doesn't create them automatically."""
    try:
        db = await get_database()
        
        # Create collections for each model
        models = [Card, CardInstance, User, GuildConfig, AuditLog, CardSubmission]
        
        for model in models:
            collection_name = model.Settings.name
            try:
                # Create collection explicitly
                await db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
            except Exception as e:
                # Collection might already exist, which is fine
                logger.debug(f"Collection {collection_name} creation: {e}")
        
        logger.info("Explicit collection creation completed")
        
    except Exception as e:
        logger.warning(f"Explicit collection creation failed: {e}")
        # Don't raise exception - collections should be created by Beanie


async def ensure_indexes() -> None:
    """Ensure all required indexes are created for optimal performance."""
    try:
        db = await get_database()
        
        # Beanie automatically creates indexes defined in model Settings.indexes
        # But we can verify or create additional indexes if needed
        
        # Get all document models for index verification
        models = [Card, CardInstance, User, GuildConfig, AuditLog, CardSubmission]
        
        for model in models:
            collection_name = model.Settings.name
            collection = db[collection_name]
            
            # Get existing indexes
            existing_indexes = await collection.list_indexes().to_list(length=None)
            index_names = [idx['name'] for idx in existing_indexes]
            
            logger.debug(f"Collection '{collection_name}' indexes: {index_names}")
        
        logger.info("Index verification completed")
        
    except Exception as e:
        logger.warning(f"Index verification failed: {e}")
        # Don't raise exception - indexes are not critical for basic functionality


async def init_mongodb(mongodb_url: Optional[str] = None) -> None:
    """Initialize MongoDB connection and Beanie ODM."""
    global mongodb_client, database
    
    if mongodb_url is None:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    database_name = os.getenv("MONGODB_DATABASE", "card_collector")
    
    logger.info(f"Attempting MongoDB connection to: {mongodb_url[:50]}...")
    logger.info(f"MongoDB database name: {database_name}")
    
    try:
        # Create MongoDB client with SSL configuration
        # For MongoDB Atlas, we need to handle SSL/TLS properly
        client_options = {
            "serverSelectionTimeoutMS": 5000,  # 5 second timeout
            "socketTimeoutMS": 5000,
            "connectTimeoutMS": 5000,
        }
        
        # If URL contains MongoDB Atlas hostnames, add SSL configuration
        if "mongodb.net" in mongodb_url or "mongodb+srv:" in mongodb_url:
            client_options.update({
                "tls": True,
                "tlsAllowInvalidCertificates": False,
                "retryWrites": True,
                "w": "majority"
            })
            logger.info("Using MongoDB Atlas configuration with TLS")
        
        mongodb_client = AsyncIOMotorClient(mongodb_url, **client_options)
        database = mongodb_client[database_name]
        
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB at {mongodb_url}")
        
        # Explicitly create database by performing a write operation
        # Some MongoDB services require explicit database creation
        logger.info(f"Creating/accessing MongoDB database: {database_name}")
        
        # Create database by creating a temporary collection
        temp_collection = database["_startup_check"]
        await temp_collection.insert_one({"startup": True, "timestamp": datetime.utcnow()})
        await temp_collection.drop()
        logger.info("Database created successfully")
        
        # Initialize Beanie with document models
        # This will create collections and indexes automatically
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
        
        # Verify collections were created/exist
        collections = await database.list_collection_names()
        logger.info(f"Available collections: {collections}")
        
        # If no collections exist, create them explicitly
        if not collections:
            logger.info("No collections found, creating them explicitly")
            await create_collections_explicitly()
        
        # Create indexes explicitly if needed (Beanie should handle this automatically)
        await ensure_indexes()
        logger.info("Database indexes verified")
        
        # Verify collections were created after Beanie initialization
        final_collections = await database.list_collection_names()
        logger.info(f"Final collections after setup: {final_collections}")
        
        if not final_collections:
            logger.warning("No collections were created - this may indicate an issue with Beanie setup")
        else:
            logger.info(f"✅ Database setup complete with {len(final_collections)} collections")
        
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


async def setup_database() -> dict:
    """
    Setup database with initial configuration if needed.
    This function can be called during first-time setup.
    """
    try:
        await init_mongodb()
        
        db = await get_database()
        
        # Check if database exists and has collections
        collections = await db.list_collection_names()
        
        result = {
            "status": "success",
            "database_name": db.name,
            "collections_created": [],
            "message": "Database setup completed"
        }
        
        if not collections:
            # Database is completely new
            logger.info("New MongoDB database detected - collections will be created on first use")
            result["message"] = "New database initialized - collections will be created automatically"
        else:
            result["collections_created"] = collections
            logger.info(f"Existing database found with collections: {collections}")
        
        # Verify health
        health = await mongodb_health_check()
        result["health"] = health
        
        return result
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Database setup failed"
        }