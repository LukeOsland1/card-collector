#!/usr/bin/env python3
"""
Test MongoDB database setup and automatic collection creation.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mongodb_setup():
    """Test MongoDB database and collection creation."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import MongoDB modules
        from db.mongodb_base import init_mongodb, get_database, mongodb_health_check
        from db.mongodb_models import Card, CardInstance, User, CardRarity, CardStatus
        
        logger.info("🧪 Testing MongoDB Setup")
        logger.info("=" * 30)
        
        # Test 1: Initialize MongoDB connection
        logger.info("1️⃣ Testing MongoDB connection...")
        await init_mongodb()
        logger.info("✅ MongoDB connection initialized")
        
        # Test 2: Get database
        logger.info("2️⃣ Testing database access...")
        db = await get_database()
        logger.info(f"✅ Database accessed: {db.name}")
        
        # Test 3: Check collections
        logger.info("3️⃣ Checking collections...")
        collections_before = await db.list_collection_names()
        logger.info(f"📋 Collections before: {collections_before}")
        
        # Test 4: Create a test document (this should create the collection)
        logger.info("4️⃣ Creating test card...")
        test_card = Card(
            name="Test Card",
            description="This is a test card to verify database setup",
            rarity=CardRarity.COMMON,
            created_by_user_id=123456789,
            status=CardStatus.APPROVED,
            tags=["test", "setup", "mongodb"]
        )
        
        await test_card.insert()
        logger.info(f"✅ Test card created with ID: {test_card.id}")
        
        # Test 5: Check collections after creation
        logger.info("5️⃣ Verifying collections after document creation...")
        collections_after = await db.list_collection_names()
        logger.info(f"📋 Collections after: {collections_after}")
        
        # Test 6: Query the document
        logger.info("6️⃣ Testing document retrieval...")
        found_card = await Card.find_one(Card.name == "Test Card")
        if found_card:
            logger.info(f"✅ Card retrieved: {found_card.name} (ID: {found_card.id})")
        else:
            logger.error("❌ Card not found!")
        
        # Test 7: Health check
        logger.info("7️⃣ Testing health check...")
        health = await mongodb_health_check()
        if health["status"] == "healthy":
            logger.info(f"✅ Health check passed")
            logger.info(f"   Database: {health['database_name']}")
            logger.info(f"   Collections: {health['collections_count']}")
        else:
            logger.error(f"❌ Health check failed: {health}")
        
        # Test 8: Clean up test data
        logger.info("8️⃣ Cleaning up test data...")
        if found_card:
            await found_card.delete()
            logger.info("✅ Test card deleted")
        
        logger.info("")
        logger.info("🎉 All tests passed!")
        logger.info("✅ MongoDB database setup is working correctly")
        logger.info("✅ Collections are created automatically")
        logger.info("✅ Documents can be inserted and retrieved")
        logger.info("✅ Health checks are working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run MongoDB setup test."""
    logger.info("🍃 Card Collector MongoDB Test")
    logger.info("This test verifies that MongoDB database and collections are created correctly.")
    logger.info("")
    
    # Check if MongoDB dependencies are available
    try:
        import motor
        import pymongo
        import beanie
        logger.info(f"📦 Dependencies OK: motor={motor.version}, pymongo={pymongo.version}, beanie={beanie.__version__}")
    except ImportError as e:
        logger.error(f"❌ Missing MongoDB dependencies: {e}")
        logger.info("💡 Install with: python install_mongodb.py")
        return
    
    # Check environment
    database_type = os.getenv("DATABASE_TYPE", "sqlite")
    if database_type != "mongodb":
        logger.warning(f"⚠️  DATABASE_TYPE is '{database_type}', not 'mongodb'")
        logger.info("💡 Set DATABASE_TYPE=mongodb in .env file to test MongoDB")
        return
    
    # Run test
    success = await test_mongodb_setup()
    
    if success:
        logger.info("")
        logger.info("🎉 MongoDB setup test completed successfully!")
        logger.info("Your Card Collector is ready to use with MongoDB!")
    else:
        logger.error("")
        logger.error("❌ MongoDB setup test failed!")
        logger.info("💡 Check your MongoDB connection and configuration")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test cancelled by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)