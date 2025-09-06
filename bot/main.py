"""Discord bot main entry point."""
import asyncio
import logging

import discord
from discord.ext import commands

from db.base import Base, async_engine

logger = logging.getLogger(__name__)


class CardBot(commands.Bot):
    """Main bot class."""

    def __init__(self):
        # Configure intents - avoid privileged intents when possible
        intents = discord.Intents.default()
        intents.guilds = True  # Required for slash commands
        # Note: message_content is a privileged intent, only enable if needed for prefix commands
        # For slash commands only, this is not required
        
        super().__init__(
            command_prefix="!",  # Fallback prefix (rarely used with slash commands)
            intents=intents,
            description="Collectible Card Management Bot"
        )

    async def setup_hook(self):
        """Setup hook called when bot is starting."""
        logger.info("Setting up bot...")

        # Create database tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")
        
        # Load command extensions
        try:
            await self.load_extension("bot.commands")
            await self.load_extension("bot.admin")
            logger.info("Loaded bot commands and admin commands")
        except Exception as e:
            logger.error(f"Failed to load commands: {e}")
            raise

    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"Bot is ready! Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")


async def main():
    """Main entry point."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        logger.error("DISCORD_BOT_TOKEN not found in environment")
        return
    
    bot = CardBot()
    
    try:
        async with bot:
            await bot.start(bot_token)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())