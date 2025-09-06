#!/usr/bin/env python3
"""
MongoDB Installation and Setup Script for Card Collector

This script helps install MongoDB dependencies and provides setup instructions.
"""

import os
import sys
import subprocess
import platform
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_command(command, description="Running command"):
    """Run a shell command and return success status."""
    try:
        logger.info(f"{description}: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {description}")
        logger.error(f"Error: {e.stderr}")
        return False


def install_python_dependencies():
    """Install Python MongoDB dependencies."""
    logger.info("📦 Installing Python MongoDB dependencies...")
    
    dependencies = [
        "motor>=3.3.0",
        "pymongo>=4.6.0", 
        "beanie>=1.24.0"
    ]
    
    for dep in dependencies:
        success = run_command(
            f"{sys.executable} -m pip install {dep}",
            f"Installing {dep}"
        )
        if not success:
            logger.error(f"Failed to install {dep}")
            return False
    
    return True


def check_mongodb_installation():
    """Check if MongoDB is installed and running."""
    logger.info("🔍 Checking MongoDB installation...")
    
    # Check if mongod is available
    try:
        result = subprocess.run(["mongod", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ MongoDB is installed")
            return True
        else:
            logger.warning("⚠️  MongoDB not found in PATH")
            return False
    except FileNotFoundError:
        logger.warning("⚠️  MongoDB not found")
        return False


def install_mongodb_instructions():
    """Provide MongoDB installation instructions for different platforms."""
    system = platform.system().lower()
    
    logger.info("📋 MongoDB Installation Instructions:")
    logger.info("=" * 50)
    
    if system == "darwin":  # macOS
        logger.info("🍎 macOS Installation:")
        logger.info("1. Using Homebrew (recommended):")
        logger.info("   brew tap mongodb/brew")
        logger.info("   brew install mongodb-community")
        logger.info("   brew services start mongodb/brew/mongodb-community")
        logger.info("")
        logger.info("2. Using Docker:")
        logger.info("   docker run -d -p 27017:27017 --name mongodb mongo:latest")
        
    elif system == "linux":
        logger.info("🐧 Linux Installation:")
        logger.info("1. Ubuntu/Debian:")
        logger.info("   sudo apt update")
        logger.info("   sudo apt install -y mongodb")
        logger.info("   sudo systemctl start mongodb")
        logger.info("   sudo systemctl enable mongodb")
        logger.info("")
        logger.info("2. Using Docker:")
        logger.info("   docker run -d -p 27017:27017 --name mongodb mongo:latest")
        
    elif system == "windows":
        logger.info("🪟 Windows Installation:")
        logger.info("1. Download MongoDB Community Server:")
        logger.info("   https://www.mongodb.com/try/download/community")
        logger.info("2. Run the installer and follow setup wizard")
        logger.info("3. MongoDB will start automatically as a service")
        logger.info("")
        logger.info("4. Using Docker:")
        logger.info("   docker run -d -p 27017:27017 --name mongodb mongo:latest")
    
    logger.info("")
    logger.info("🔗 Alternative: Free MongoDB Atlas Cloud:")
    logger.info("   https://www.mongodb.com/atlas")


def test_mongodb_connection():
    """Test MongoDB connection."""
    logger.info("🧪 Testing MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        
        # Try to connect to local MongoDB
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        
        logger.info("✅ MongoDB connection successful!")
        
        # Get database info
        server_info = client.server_info()
        logger.info(f"📊 MongoDB version: {server_info['version']}")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.info("💡 Make sure MongoDB is running on localhost:27017")
        return False


def create_mongodb_config():
    """Create or update .env file with MongoDB configuration."""
    logger.info("⚙️  Configuring MongoDB settings...")
    
    env_file = ".env"
    mongodb_config = """
# ===== MONGODB CONFIGURATION =====
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=card_collector
"""
    
    if os.path.exists(env_file):
        # Read existing .env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if MongoDB config already exists
        if "DATABASE_TYPE=mongodb" in content:
            logger.info("✅ MongoDB configuration already exists in .env")
        else:
            # Add MongoDB configuration
            with open(env_file, 'a') as f:
                f.write(mongodb_config)
            logger.info("✅ Added MongoDB configuration to .env")
    else:
        # Create new .env file with MongoDB config
        with open(env_file, 'w') as f:
            f.write(mongodb_config.strip())
        logger.info("✅ Created .env file with MongoDB configuration")


def main():
    """Main setup function."""
    logger.info("🚀 Card Collector MongoDB Setup")
    logger.info("=" * 40)
    
    # Step 1: Install Python dependencies
    if not install_python_dependencies():
        logger.error("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Step 2: Check MongoDB installation
    mongodb_installed = check_mongodb_installation()
    
    if not mongodb_installed:
        install_mongodb_instructions()
        logger.info("")
        logger.info("⚠️  Please install MongoDB first, then run this script again")
        sys.exit(1)
    
    # Step 3: Test MongoDB connection
    if not test_mongodb_connection():
        logger.info("")
        logger.info("⚠️  MongoDB is installed but not running or not accessible")
        install_mongodb_instructions()
        sys.exit(1)
    
    # Step 4: Create MongoDB configuration
    create_mongodb_config()
    
    logger.info("")
    logger.info("🎉 MongoDB setup complete!")
    logger.info("=" * 30)
    logger.info("✅ Python dependencies installed")
    logger.info("✅ MongoDB connection tested")
    logger.info("✅ Configuration updated")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Run: python run.py")
    logger.info("2. Visit: http://localhost:8080")
    logger.info("3. Check health: http://localhost:8080/api/health")


if __name__ == "__main__":
    main()