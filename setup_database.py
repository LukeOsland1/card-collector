#!/usr/bin/env python3
"""
Database Setup Script for Card Collector

This script initializes the MongoDB database and verifies the setup.
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


async def main():
    """Main database setup function."""
    logger.info("🍃 Card Collector Database Setup")
    logger.info("=" * 40)
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check database configuration
        database_type = os.getenv("DATABASE_TYPE", "sqlite").lower()
        logger.info(f"📊 Database type: {database_type}")
        
        if database_type == "mongodb":
            # Setup MongoDB
            from db.mongodb_base import setup_database, init_mongodb
            
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            mongodb_database = os.getenv("MONGODB_DATABASE", "card_collector")
            
            logger.info(f"🔗 MongoDB URL: {mongodb_url}")
            logger.info(f"🗄️  Database name: {mongodb_database}")
            
            # Test connection first
            try:
                from pymongo import MongoClient
                client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
                client.admin.command('ping')
                client.close()
                logger.info("✅ MongoDB connection successful")
            except Exception as e:
                logger.error(f"❌ MongoDB connection failed: {e}")
                logger.info("💡 Make sure MongoDB is running")
                logger.info("   Local: mongod --dbpath /path/to/data")
                logger.info("   Docker: docker run -d -p 27017:27017 mongo")
                logger.info("   Atlas: Check your connection string")
                return
            
            # Setup database
            logger.info("🔄 Setting up MongoDB database...")
            result = await setup_database()
            
            if result["status"] == "success":
                logger.info("✅ Database setup successful!")
                logger.info(f"📋 Database: {result['database_name']}")
                
                collections = result.get("collections_created", [])
                if collections:
                    logger.info(f"📂 Existing collections: {', '.join(collections)}")
                else:
                    logger.info("📂 Collections will be created automatically on first use")
                
                # Show health status
                health = result.get("health", {})
                if health.get("status") == "healthy":
                    logger.info(f"💾 Data size: {health.get('data_size', 0)} bytes")
                    logger.info(f"💿 Storage size: {health.get('storage_size', 0)} bytes")
                
                logger.info("")
                logger.info("🎉 MongoDB database is ready!")
                logger.info("Next steps:")
                logger.info("1. Run: python run.py")
                logger.info("2. Visit: http://localhost:8080")
                logger.info("3. Check: http://localhost:8080/api/health")
                
            else:
                logger.error(f"❌ Database setup failed: {result['message']}")
                return
        
        elif database_type in ["sqlite", "postgresql"]:
            # SQL database setup
            logger.info("🗄️  SQL database detected")
            
            from db.base import engine, Base
            from db.models import Card  # Import to ensure tables are defined
            
            logger.info("🔄 Creating SQL database tables...")
            
            # Create tables
            Base.metadata.create_all(bind=engine)
            
            logger.info("✅ SQL database tables created!")
            logger.info("🎉 SQL database is ready!")
            logger.info("Next steps:")
            logger.info("1. Run: python run.py")
            logger.info("2. Visit: http://localhost:8080")
        
        else:
            logger.error(f"❌ Unknown database type: {database_type}")
            logger.info("💡 Set DATABASE_TYPE to one of: mongodb, sqlite, postgresql")
            return
    
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("💡 Install dependencies:")
        logger.info("   python install_deps.py")
        logger.info("   or: pip install -r requirements.txt")
    
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        logger.info("💡 Check your configuration and try again")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Setup cancelled by user")
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)