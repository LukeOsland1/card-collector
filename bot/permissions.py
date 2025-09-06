"""Permission system for Discord bot commands."""
import logging
from typing import Optional, List

import discord
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import get_db
from db.crud import GuildConfigCRUD, UserCRUD
from db.models import User
from .embeds import create_error_embed

logger = logging.getLogger(__name__)


class PermissionLevel:
    """Permission level constants."""
    USER = 1
    MODERATOR = 2
    ADMIN = 3
    OWNER = 4


async def get_user_permission_level(
    interaction: discord.Interaction,
    db: AsyncSession,
    user_id: Optional[int] = None
) -> int:
    """Get the permission level for a user in the current guild."""
    if user_id is None:
        user_id = interaction.user.id
    
    guild = interaction.guild
    if not guild:
        # DM commands - only basic user permissions
        return PermissionLevel.USER
    
    member = guild.get_member(user_id) or interaction.user
    
    # Bot owner has highest permission
    app_info = await interaction.client.application_info()
    if user_id == app_info.owner.id:
        return PermissionLevel.OWNER
    
    # Guild owner has admin permission
    if user_id == guild.owner_id:
        return PermissionLevel.ADMIN
    
    # Check if user has administrator permission
    if isinstance(member, discord.Member) and member.guild_permissions.administrator:
        return PermissionLevel.ADMIN
    
    # Check guild-specific configuration
    try:
        guild_config = await GuildConfigCRUD.get_or_create(db, guild.id)
        
        # Check admin roles
        if guild_config.admin_role_ids:
            admin_roles = set(guild_config.admin_role_ids)
            user_roles = {role.id for role in member.roles} if isinstance(member, discord.Member) else set()
            if admin_roles.intersection(user_roles):
                return PermissionLevel.ADMIN
        
        # Check moderator roles
        if guild_config.mod_role_ids:
            mod_roles = set(guild_config.mod_role_ids)
            user_roles = {role.id for role in member.roles} if isinstance(member, discord.Member) else set()
            if mod_roles.intersection(user_roles):
                return PermissionLevel.MODERATOR
        
        # Check admin users
        if guild_config.admin_user_ids and user_id in guild_config.admin_user_ids:
            return PermissionLevel.ADMIN
        
        # Check moderator users
        if guild_config.mod_user_ids and user_id in guild_config.mod_user_ids:
            return PermissionLevel.MODERATOR
        
    except Exception as e:
        logger.error(f"Error checking guild permissions: {e}")
    
    # Check Discord permissions as fallback
    if isinstance(member, discord.Member):
        # Users with manage_messages can moderate
        if member.guild_permissions.manage_messages:
            return PermissionLevel.MODERATOR
        
        # Users with manage_roles can admin (but not owner-level)
        if member.guild_permissions.manage_roles:
            return PermissionLevel.ADMIN
    
    return PermissionLevel.USER


async def check_permissions(
    interaction: discord.Interaction,
    db: AsyncSession,
    require_mod: bool = False,
    require_admin: bool = False,
    require_owner: bool = False,
    user_id: Optional[int] = None
) -> bool:
    """Check if user has required permissions."""
    permission_level = await get_user_permission_level(interaction, db, user_id)
    
    if require_owner:
        return permission_level >= PermissionLevel.OWNER
    elif require_admin:
        return permission_level >= PermissionLevel.ADMIN
    elif require_mod:
        return permission_level >= PermissionLevel.MODERATOR
    else:
        return permission_level >= PermissionLevel.USER


async def get_permission_error_message(
    interaction: discord.Interaction,
    require_mod: bool = False,
    require_admin: bool = False,
    require_owner: bool = False
) -> str:
    """Get appropriate error message for permission failure."""
    if require_owner:
        return "This command can only be used by the bot owner."
    elif require_admin:
        return "This command requires administrator permissions."
    elif require_mod:
        return "This command requires moderator permissions or higher."
    else:
        return "You don't have permission to use this command."


async def is_guild_setup(db: AsyncSession, guild_id: int) -> bool:
    """Check if a guild has been properly configured."""
    try:
        guild_config = await GuildConfigCRUD.get(db, guild_id)
        return guild_config is not None
    except Exception:
        return False


def get_permission_level_name(level: int) -> str:
    """Get human-readable name for permission level."""
    names = {
        PermissionLevel.USER: "User",
        PermissionLevel.MODERATOR: "Moderator", 
        PermissionLevel.ADMIN: "Administrator",
        PermissionLevel.OWNER: "Bot Owner"
    }
    return names.get(level, "Unknown")


async def get_user_permissions_info(
    interaction: discord.Interaction,
    db: AsyncSession,
    user_id: Optional[int] = None
) -> dict:
    """Get detailed permission information for a user."""
    if user_id is None:
        user_id = interaction.user.id
    
    guild = interaction.guild
    permission_level = await get_user_permission_level(interaction, db, user_id)
    
    info = {
        "user_id": user_id,
        "guild_id": guild.id if guild else None,
        "permission_level": permission_level,
        "permission_name": get_permission_level_name(permission_level),
        "can_moderate": permission_level >= PermissionLevel.MODERATOR,
        "can_admin": permission_level >= PermissionLevel.ADMIN,
        "is_owner": permission_level >= PermissionLevel.OWNER,
    }
    
    if guild:
        member = guild.get_member(user_id)
        if member:
            info["roles"] = [role.name for role in member.roles if role != guild.default_role]
            info["discord_permissions"] = {
                "administrator": member.guild_permissions.administrator,
                "manage_roles": member.guild_permissions.manage_roles,
                "manage_messages": member.guild_permissions.manage_messages,
                "manage_guild": member.guild_permissions.manage_guild,
            }
    
    return info


class PermissionChecks:
    """Decorators and checks for command permissions."""
    
    @staticmethod
    def require_moderator():
        """Decorator to require moderator permissions."""
        def decorator(func):
            async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
                async for db in get_db():
                    has_permission = await check_permissions(interaction, db, require_mod=True)
                    if not has_permission:
                        error_msg = await get_permission_error_message(interaction, require_mod=True)
                        embed = create_error_embed(error_msg)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                return await func(self, interaction, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def require_admin():
        """Decorator to require admin permissions."""
        def decorator(func):
            async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
                async for db in get_db():
                    has_permission = await check_permissions(interaction, db, require_admin=True)
                    if not has_permission:
                        error_msg = await get_permission_error_message(interaction, require_admin=True)
                        embed = create_error_embed(error_msg)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                return await func(self, interaction, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def require_owner():
        """Decorator to require owner permissions."""
        def decorator(func):
            async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
                async for db in get_db():
                    has_permission = await check_permissions(interaction, db, require_owner=True)
                    if not has_permission:
                        error_msg = await get_permission_error_message(interaction, require_owner=True)
                        embed = create_error_embed(error_msg)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                return await func(self, interaction, *args, **kwargs)
            return wrapper
        return decorator


async def setup_guild_permissions(
    db: AsyncSession,
    guild_id: int,
    admin_role_ids: Optional[List[int]] = None,
    mod_role_ids: Optional[List[int]] = None,
    admin_user_ids: Optional[List[int]] = None,
    mod_user_ids: Optional[List[int]] = None
) -> bool:
    """Setup permission configuration for a guild."""
    try:
        guild_config = await GuildConfigCRUD.get_or_create(db, guild_id)
        
        if admin_role_ids is not None:
            guild_config.admin_role_ids = admin_role_ids
        if mod_role_ids is not None:
            guild_config.mod_role_ids = mod_role_ids
        if admin_user_ids is not None:
            guild_config.admin_user_ids = admin_user_ids
        if mod_user_ids is not None:
            guild_config.mod_user_ids = mod_user_ids
        
        await db.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error setting up guild permissions: {e}")
        return False


async def can_user_assign_cards(
    interaction: discord.Interaction,
    db: AsyncSession,
    user_id: Optional[int] = None
) -> bool:
    """Check if user can assign cards to others."""
    return await check_permissions(interaction, db, require_mod=True, user_id=user_id)


async def can_user_approve_cards(
    interaction: discord.Interaction,
    db: AsyncSession,
    user_id: Optional[int] = None
) -> bool:
    """Check if user can approve/reject card submissions."""
    return await check_permissions(interaction, db, require_mod=True, user_id=user_id)


async def can_user_create_cards(
    interaction: discord.Interaction,
    db: AsyncSession,
    user_id: Optional[int] = None
) -> bool:
    """Check if user can create cards directly (bypass approval)."""
    return await check_permissions(interaction, db, require_mod=True, user_id=user_id)


async def can_user_remove_cards(
    interaction: discord.Interaction,
    db: AsyncSession,
    user_id: Optional[int] = None
) -> bool:
    """Check if user can remove card instances."""
    return await check_permissions(interaction, db, require_mod=True, user_id=user_id)


async def can_user_configure_guild(
    interaction: discord.Interaction,
    db: AsyncSession,
    user_id: Optional[int] = None
) -> bool:
    """Check if user can configure guild settings."""
    return await check_permissions(interaction, db, require_admin=True, user_id=user_id)