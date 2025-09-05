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
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True

        super().__init__(
            command_prefix="!",
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