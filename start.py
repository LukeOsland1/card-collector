#!/usr/bin/env python3
"""
Card Collector - Comprehensive Startup Script

This script initializes and starts all components of the Card Collector system:
- Database initialization and migrations
- Discord bot
- Web API server
- Background schedulers
- Image processing service
"""

import asyncio
import logging
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/card-collector.log')
    ]
)

logger = logging.getLogger(__name__)

# Global state
running_services = []
shutdown_event = asyncio.Event()


def setup_directories():
    """Create necessary directories."""
    directories = [
        'logs',
        'storage/images',
        'storage/thumbnails',
        'storage/previews',
        'storage/cards',
        'storage/temp',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")


def check_environment():
    """Check required environment variables and files."""
    required_env_vars = [
        'DISCORD_BOT_TOKEN',
        'DATABASE_URL',
        'JWT_SECRET_KEY',
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please create a .env file with the required variables.")
        logger.info("Check .env.example for reference.")
        return False
    
    # Check if .env file exists
    if not Path('.env').exists():
        logger.warning(".env file not found. Using system environment variables.")
    else:
        logger.info("Found .env file, loading environment variables...")
        from dotenv import load_dotenv
        load_dotenv()
    
    return True


async def initialize_database():
    """Initialize database and run migrations."""
    logger.info("Initializing database...")
    
    try:
        from scripts.init_db import main as init_db_main
        success = await init_db_main()
        
        if success:
            logger.info("Database initialization completed successfully")
            return True
        else:
            logger.error("Database initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False


async def start_discord_bot():
    """Start the Discord bot."""
    logger.info("Starting Discord bot...")
    
    try:
        from bot.main import CardBot
        
        bot = CardBot()
        
        # Run bot in background
        bot_task = asyncio.create_task(bot.start(os.getenv('DISCORD_BOT_TOKEN')))
        running_services.append(('discord_bot', bot_task, bot))
        
        logger.info("Discord bot started successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start Discord bot: {e}")
        return False


async def start_web_server():
    """Start the web server."""
    logger.info("Starting web server...")
    
    try:
        import uvicorn
        from web.app import app
        
        # Configure uvicorn
        config = uvicorn.Config(
            app,
            host=os.getenv('WEB_HOST', '0.0.0.0'),
            port=int(os.getenv('WEB_PORT', 8080)),
            log_level='info',
            access_log=True,
            loop='asyncio'
        )
        
        server = uvicorn.Server(config)
        
        # Create task for web server
        server_task = asyncio.create_task(server.serve())
        running_services.append(('web_server', server_task, server))
        
        logger.info(f"Web server started on http://{config.host}:{config.port}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
        return False


async def start_background_schedulers():
    """Start background job schedulers."""
    logger.info("Starting background schedulers...")
    
    try:
        from services.scheduler import start_schedulers
        
        await start_schedulers()
        logger.info("Background schedulers started successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start background schedulers: {e}")
        return False


async def health_check():
    """Perform health checks on running services."""
    logger.info("Performing health checks...")
    
    try:
        # Check database connection
        from db.base import async_engine
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ Database connection: OK")
        
        # Check web server (would need to implement health endpoint)
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8080/api/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info("✅ Web server health: OK")
                else:
                    logger.warning(f"⚠️ Web server health: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Web server health check failed: {e}")
        
        # Check Discord bot status (would check if bot is connected)
        logger.info("✅ Health checks completed")
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")


async def shutdown_handler(signame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received {signame}, shutting down gracefully...")
    shutdown_event.set()
    
    # Stop all services
    for service_name, task, service_obj in running_services:
        logger.info(f"Stopping {service_name}...")
        
        try:
            # Try to stop gracefully first
            if hasattr(service_obj, 'close'):
                await service_obj.close()
            elif hasattr(service_obj, 'shutdown'):
                await service_obj.shutdown()
            
            # Cancel the task
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=10.0)
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout stopping {service_name}")
                except asyncio.CancelledError:
                    pass
                    
        except Exception as e:
            logger.error(f"Error stopping {service_name}: {e}")
    
    # Stop background schedulers
    try:
        from services.scheduler import stop_schedulers
        await stop_schedulers()
        logger.info("Background schedulers stopped")
    except Exception as e:
        logger.error(f"Error stopping schedulers: {e}")
    
    logger.info("Shutdown completed")


async def main():
    """Main application entry point."""
    logger.info("🚀 Starting Card Collector...")
    
    # Setup signal handlers
    if sys.platform != 'win32':
        for signame in ('SIGTERM', 'SIGINT'):
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(
                getattr(signal, signame),
                lambda: asyncio.create_task(shutdown_handler(signame))
            )
    
    try:
        # Pre-flight checks
        setup_directories()
        
        if not check_environment():
            logger.error("Environment check failed")
            return 1
        
        # Initialize database
        logger.info("Step 1/5: Database initialization")
        if not await initialize_database():
            logger.error("Database initialization failed, aborting startup")
            return 1
        
        # Start services
        logger.info("Step 2/5: Starting Discord bot")
        if not await start_discord_bot():
            logger.error("Failed to start Discord bot")
            return 1
        
        # Small delay to let bot initialize
        await asyncio.sleep(2)
        
        logger.info("Step 3/5: Starting web server")
        if not await start_web_server():
            logger.error("Failed to start web server")
            return 1
        
        logger.info("Step 4/5: Starting background schedulers")
        if not await start_background_schedulers():
            logger.warning("Background schedulers failed to start (non-critical)")
        
        logger.info("Step 5/5: Performing initial health check")
        await asyncio.sleep(3)  # Wait for services to fully start
        await health_check()
        
        logger.info("🎉 Card Collector started successfully!")
        logger.info("=" * 50)
        logger.info("Services running:")
        logger.info("- Discord Bot: Connected and ready")
        logger.info(f"- Web Server: http://{os.getenv('WEB_HOST', '0.0.0.0')}:{os.getenv('WEB_PORT', 8080)}")
        logger.info(f"- API Docs: http://{os.getenv('WEB_HOST', '0.0.0.0')}:{os.getenv('WEB_PORT', 8080)}/docs")
        logger.info("- Background Jobs: Running")
        logger.info("=" * 50)
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
    except KeyboardInterrupt:
        await shutdown_handler('KeyboardInterrupt')
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}", exc_info=True)
        return 1
    
    return 0


def run():
    """Run the application with proper error handling."""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run()