"""Admin commands for Discord bot."""
import logging
from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import get_db
from db.crud import AuditLogCRUD, CardCRUD, GuildConfigCRUD, UserCRUD
from db.models import CardStatus

from .embeds import (
    create_error_embed,
    create_info_embed,
    create_success_embed,
    PaginationView,
)
from .permissions import (
    check_permissions,
    get_permission_error_message,
    get_user_permissions_info,
    setup_guild_permissions,
)

logger = logging.getLogger(__name__)


class AdminCommands(commands.GroupCog, name="admin"):
    """Administrative commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setup")
    @app_commands.describe(
        admin_roles="Admin roles (comma-separated role mentions or IDs)",
        mod_roles="Moderator roles (comma-separated role mentions or IDs)",
        admin_users="Admin users (comma-separated user mentions or IDs)",
        mod_users="Moderator users (comma-separated user mentions or IDs)"
    )
    async def setup_permissions(
        self,
        interaction: discord.Interaction,
        admin_roles: Optional[str] = None,
        mod_roles: Optional[str] = None,
        admin_users: Optional[str] = None,
        mod_users: Optional[str] = None
    ):
        """Setup permission roles and users for this guild (admin only)."""
        await interaction.response.defer(ephemeral=True)

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_admin=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_admin=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Parse role and user IDs
                admin_role_ids = self._parse_ids(admin_roles) if admin_roles else None
                mod_role_ids = self._parse_ids(mod_roles) if mod_roles else None
                admin_user_ids = self._parse_ids(admin_users) if admin_users else None
                mod_user_ids = self._parse_ids(mod_users) if mod_users else None

                # Setup permissions
                success = await setup_guild_permissions(
                    db,
                    interaction.guild_id,
                    admin_role_ids=admin_role_ids,
                    mod_role_ids=mod_role_ids,
                    admin_user_ids=admin_user_ids,
                    mod_user_ids=mod_user_ids,
                )

                if success:
                    # Log action
                    await AuditLogCRUD.create(
                        db,
                        actor_user_id=interaction.user.id,
                        action="guild_permissions_setup",
                        target_type="guild_config",
                        target_id=str(interaction.guild_id),
                        meta={
                            "admin_roles": admin_role_ids,
                            "mod_roles": mod_role_ids,
                            "admin_users": admin_user_ids,
                            "mod_users": mod_user_ids,
                        }
                    )

                    embed = create_success_embed(
                        "Guild permissions have been configured successfully!"
                    )
                else:
                    embed = create_error_embed(
                        "Failed to configure guild permissions."
                    )

                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error setting up permissions: {e}")
            embed = create_error_embed("An error occurred while setting up permissions.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="permissions")
    @app_commands.describe(user="User to check permissions for (optional)")
    async def check_user_permissions(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None
    ):
        """Check permission level for a user (admin only)."""
        await interaction.response.defer(ephemeral=True)

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_admin=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_admin=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                target_user = user or interaction.user
                
                # Get permission info
                perm_info = await get_user_permissions_info(
                    interaction, db, target_user.id
                )

                embed = discord.Embed(
                    title=f"🔐 Permission Info: {target_user.display_name}",
                    color=0x3498db
                )

                embed.add_field(
                    name="Permission Level",
                    value=f"**{perm_info['permission_name']}** (Level {perm_info['permission_level']})",
                    inline=False
                )

                embed.add_field(
                    name="Capabilities",
                    value=(
                        f"{'✅' if perm_info['can_moderate'] else '❌'} Can moderate\n"
                        f"{'✅' if perm_info['can_admin'] else '❌'} Can admin\n"
                        f"{'✅' if perm_info['is_owner'] else '❌'} Is bot owner"
                    ),
                    inline=True
                )

                if "roles" in perm_info:
                    roles_text = ", ".join(perm_info["roles"][:10])
                    if len(perm_info["roles"]) > 10:
                        roles_text += f" +{len(perm_info['roles']) - 10} more"
                    
                    embed.add_field(
                        name="Discord Roles",
                        value=roles_text or "None",
                        inline=False
                    )

                if "discord_permissions" in perm_info:
                    dp = perm_info["discord_permissions"]
                    embed.add_field(
                        name="Discord Permissions",
                        value=(
                            f"{'✅' if dp['administrator'] else '❌'} Administrator\n"
                            f"{'✅' if dp['manage_roles'] else '❌'} Manage Roles\n"
                            f"{'✅' if dp['manage_messages'] else '❌'} Manage Messages"
                        ),
                        inline=True
                    )

                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            embed = create_error_embed("An error occurred while checking permissions.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="stats")
    async def guild_stats(self, interaction: discord.Interaction):
        """Show guild statistics (admin only)."""
        await interaction.response.defer(ephemeral=True)

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_admin=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_admin=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Get statistics
                total_cards = await db.scalar("SELECT COUNT(*) FROM cards")
                approved_cards = await db.scalar(
                    "SELECT COUNT(*) FROM cards WHERE status = 'approved'"
                )
                submitted_cards = await db.scalar(
                    "SELECT COUNT(*) FROM cards WHERE status = 'submitted'"
                )
                total_instances = await db.scalar(
                    "SELECT COUNT(*) FROM card_instances WHERE removed_at IS NULL"
                )
                total_users = await db.scalar("SELECT COUNT(*) FROM users")

                embed = discord.Embed(
                    title="📊 Guild Statistics",
                    color=0x3498db
                )

                embed.add_field(
                    name="Cards",
                    value=(
                        f"**Total:** {total_cards}\n"
                        f"**Approved:** {approved_cards}\n"
                        f"**Pending:** {submitted_cards}"
                    ),
                    inline=True
                )

                embed.add_field(
                    name="Collection",
                    value=(
                        f"**Active Instances:** {total_instances}\n"
                        f"**Total Users:** {total_users}"
                    ),
                    inline=True
                )

                embed.set_footer(text=f"Guild ID: {interaction.guild_id}")

                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting guild stats: {e}")
            embed = create_error_embed("An error occurred while getting statistics.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="audit")
    @app_commands.describe(
        user="User to filter audit logs by (optional)",
        action="Action type to filter by (optional)",
        days="Days to look back (default: 7)"
    )
    async def audit_logs(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None,
        action: Optional[str] = None,
        days: int = 7
    ):
        """View audit logs (admin only)."""
        await interaction.response.defer(ephemeral=True)

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_admin=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_admin=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Get audit logs
                if user:
                    logs = await AuditLogCRUD.get_user_actions(
                        db, user.id, limit=50, actions=[action] if action else None
                    )
                else:
                    logs = await AuditLogCRUD.get_recent_actions(
                        db, limit=50, action=action, days=days
                    )

                if not logs:
                    embed = create_info_embed("Audit Logs", "No audit logs found matching the criteria.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Create paginated embeds
                logs_per_page = 10
                embeds = []
                total_pages = (len(logs) + logs_per_page - 1) // logs_per_page

                for page in range(total_pages):
                    start_idx = page * logs_per_page
                    end_idx = start_idx + logs_per_page
                    page_logs = logs[start_idx:end_idx]

                    embed = discord.Embed(
                        title=f"📋 Audit Logs (Page {page + 1}/{total_pages})",
                        color=0x3498db
                    )

                    for log in page_logs:
                        user_mention = f"<@{log.actor_user_id}>" if log.actor_user_id != 0 else "System"
                        timestamp = discord.utils.format_dt(log.created_at, style='R')
                        
                        value = f"**Actor:** {user_mention}\n**When:** {timestamp}"
                        if log.target_type and log.target_id:
                            value += f"\n**Target:** {log.target_type} `{log.target_id[:8]}...`"

                        embed.add_field(
                            name=f"🔸 {log.action.replace('_', ' ').title()}",
                            value=value,
                            inline=False
                        )

                    embeds.append(embed)

                if len(embeds) == 1:
                    await interaction.followup.send(embed=embeds[0], ephemeral=True)
                else:
                    view = PaginationView(embeds)
                    await interaction.followup.send(embed=embeds[0], view=view, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            embed = create_error_embed("An error occurred while getting audit logs.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="bulk-approve")
    @app_commands.describe(count="Number of oldest submitted cards to approve (max 10)")
    async def bulk_approve_cards(self, interaction: discord.Interaction, count: int = 5):
        """Bulk approve the oldest submitted cards (admin only)."""
        await interaction.response.defer(ephemeral=True)

        if count <= 0 or count > 10:
            embed = create_error_embed("Count must be between 1 and 10.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_admin=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_admin=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Get submitted cards
                submitted_cards = await CardCRUD.get_all(
                    db, status=CardStatus.SUBMITTED, limit=count
                )

                if not submitted_cards:
                    embed = create_info_embed("Bulk Approve", "No submitted cards found.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                approved_count = 0
                approved_names = []

                for card in submitted_cards:
                    approved_card = await CardCRUD.approve(db, card.id, interaction.user.id)
                    if approved_card:
                        approved_count += 1
                        approved_names.append(card.name)

                        # Log action
                        await AuditLogCRUD.create(
                            db,
                            actor_user_id=interaction.user.id,
                            action="card_bulk_approved",
                            target_type="card",
                            target_id=card.id,
                            meta={
                                "name": card.name,
                                "bulk_operation": True,
                                "guild_id": interaction.guild_id,
                            }
                        )

                if approved_count > 0:
                    embed = create_success_embed(
                        f"Bulk approved {approved_count} cards:\n" +
                        "\n".join([f"• {name}" for name in approved_names])
                    )
                else:
                    embed = create_error_embed("No cards were approved.")

                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error bulk approving cards: {e}")
            embed = create_error_embed("An error occurred while bulk approving cards.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="config")
    async def guild_config(self, interaction: discord.Interaction):
        """Show guild configuration (admin only)."""
        await interaction.response.defer(ephemeral=True)

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_admin=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_admin=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Get guild config
                config = await GuildConfigCRUD.get_or_create(db, interaction.guild_id)

                embed = discord.Embed(
                    title="⚙️ Guild Configuration",
                    color=0x3498db
                )

                # Admin roles
                admin_roles_text = "None"
                if config.admin_role_ids:
                    admin_roles_text = " ".join([f"<@&{role_id}>" for role_id in config.admin_role_ids])

                embed.add_field(
                    name="Admin Roles",
                    value=admin_roles_text,
                    inline=False
                )

                # Mod roles
                mod_roles_text = "None"
                if config.mod_role_ids:
                    mod_roles_text = " ".join([f"<@&{role_id}>" for role_id in config.mod_role_ids])

                embed.add_field(
                    name="Moderator Roles",
                    value=mod_roles_text,
                    inline=False
                )

                # Admin users
                admin_users_text = "None"
                if config.admin_user_ids:
                    admin_users_text = " ".join([f"<@{user_id}>" for user_id in config.admin_user_ids])

                embed.add_field(
                    name="Admin Users",
                    value=admin_users_text,
                    inline=False
                )

                # Mod users
                mod_users_text = "None"
                if config.mod_user_ids:
                    mod_users_text = " ".join([f"<@{user_id}>" for user_id in config.mod_user_ids])

                embed.add_field(
                    name="Moderator Users",
                    value=mod_users_text,
                    inline=False
                )

                embed.set_footer(text=f"Guild ID: {interaction.guild_id}")

                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting guild config: {e}")
            embed = create_error_embed("An error occurred while getting guild configuration.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    def _parse_ids(self, id_string: str) -> List[int]:
        """Parse comma-separated IDs from string."""
        if not id_string:
            return []
        
        ids = []
        for item in id_string.split(','):
            item = item.strip()
            # Remove mention formatting
            item = item.replace('<@&', '').replace('<@', '').replace('>', '')
            try:
                ids.append(int(item))
            except ValueError:
                continue
        
        return ids


async def setup(bot: commands.Bot):
    """Setup function for the admin cog."""
    await bot.add_cog(AdminCommands(bot))