#!/usr/bin/env python3
"""
Card Collector - Quick Start Script

Simple script to run the Card Collector system.
For full features, use start.py
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


def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    try:
        import dotenv
    except ImportError:
        missing_deps.append("python-dotenv")
    
    try:
        import discord
    except ImportError:
        missing_deps.append("discord.py")
    
    try:
        import fastapi
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing_deps.append("uvicorn")
    
    try:
        import greenlet
    except ImportError:
        missing_deps.append("greenlet")
    
    if missing_deps:
        logger.error("Missing required dependencies:")
        for dep in missing_deps:
            logger.error(f"  - {dep}")
        logger.error("\nPlease install dependencies:")
        logger.error("  python install_deps.py")
        logger.error("\nOr manually:")
        logger.error("  pip install -r requirements.txt")
        return False
    
    return True


async def quick_start():
    """Quick start for development."""
    # Check dependencies first
    if not check_dependencies():
        return
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception as e:
        logger.error(f"Failed to load .env file: {e}")
        logger.info("Continuing without .env file...")
    
    # Check essential environment variables
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    if not bot_token:
        logger.error("DISCORD_BOT_TOKEN not found in environment")
        logger.info("Please:")
        logger.info("1. Create a .env file (copy from env.example)")
        logger.info("2. Set DISCORD_BOT_TOKEN=your_actual_bot_token")
        logger.info("3. Get your bot token from: https://discord.com/developers/applications")
        return
    
    # Check for placeholder/test tokens
    if bot_token.startswith(("test_", "your_", "placeholder_", "example_", "demo_")):
        logger.error("Placeholder Discord bot token detected")
        logger.info("You're using a test/placeholder token. Please:")
        logger.info("1. Go to: https://discord.com/developers/applications")
        logger.info("2. Create a new application or select existing one")
        logger.info("3. Go to 'Bot' section and copy the real bot token")
        logger.info("4. Update your .env file: DISCORD_BOT_TOKEN=your_real_token_here")
        logger.info("5. Run the application again")
        return
    
    logger.info("Starting Card Collector in development mode...")
    
    # Initialize database quickly
    try:
        logger.info("Initializing database...")
        from db.base import Base, async_engine
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        if "greenlet" in str(e):
            logger.error("Missing greenlet dependency. Please run:")
            logger.error("  python3 install_deps.py")
            logger.error("Or manually: pip3 install greenlet")
        elif "aiosqlite" in str(e):
            logger.error("Missing aiosqlite dependency. Please run:")
            logger.error("  python3 install_deps.py")
            logger.error("Or manually: pip3 install aiosqlite")
        return
    
    # Start bot and web server concurrently
    tasks = []
    
    # Start Discord bot
    try:
        from bot.main import CardBot
        bot = CardBot()
        bot_task = asyncio.create_task(bot.start(bot_token))
        tasks.append(bot_task)
        logger.info("Discord bot starting...")
    except Exception as e:
        logger.error(f"Failed to start Discord bot: {e}")
        if "LoginFailure" in str(e) or "Improper token" in str(e) or "401 Unauthorized" in str(e):
            logger.error("Discord bot authentication failed!")
            logger.info("Your bot token is invalid. Please:")
            logger.info("1. Go to: https://discord.com/developers/applications")
            logger.info("2. Select your application")
            logger.info("3. Go to 'Bot' section")
            logger.info("4. Click 'Reset Token' if needed")
            logger.info("5. Copy the new token")
            logger.info("6. Update .env file: DISCORD_BOT_TOKEN=your_new_token_here")
        elif "PrivilegedIntentsRequired" in str(e):
            logger.error("Discord privileged intents error!")
            logger.info("The bot needs privileged intents enabled. Please:")
            logger.info("1. Go to: https://discord.com/developers/applications")
            logger.info("2. Select your application")
            logger.info("3. Go to 'Bot' section")
            logger.info("4. Scroll down to 'Privileged Gateway Intents'")
            logger.info("5. Enable 'Message Content Intent' if you need prefix commands")
            logger.info("6. Click 'Save Changes'")
            logger.info("7. Run the application again")
            logger.info("\nNote: For slash commands only, this intent is not needed.")
        return
    
    # Start web server
    try:
        import uvicorn
        from web.app import app
        
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=8080,
            log_level="info"
        )
        server = uvicorn.Server(config)
        web_task = asyncio.create_task(server.serve())
        tasks.append(web_task)
        logger.info("Web server starting on http://127.0.0.1:8080")
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        return
    
    logger.info("Card Collector is running!")
    logger.info("- Bot: Check Discord for slash commands")
    logger.info("- Web: http://127.0.0.1:8080")
    logger.info("- API: http://127.0.0.1:8080/docs")
    logger.info("Press Ctrl+C to stop")
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        for task in tasks:
            task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(quick_start())
    except KeyboardInterrupt:
        pass