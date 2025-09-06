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


async def quick_start():
    """Quick start for development."""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check essential environment variables
    if not os.getenv('DISCORD_BOT_TOKEN'):
        logger.error("DISCORD_BOT_TOKEN not found in environment")
        logger.info("Please set your Discord bot token in .env file")
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
        return
    
    # Start bot and web server concurrently
    tasks = []
    
    # Start Discord bot
    try:
        from bot.main import CardBot
        bot = CardBot()
        bot_task = asyncio.create_task(bot.start(os.getenv('DISCORD_BOT_TOKEN')))
        tasks.append(bot_task)
        logger.info("Discord bot starting...")
    except Exception as e:
        logger.error(f"Failed to start Discord bot: {e}")
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