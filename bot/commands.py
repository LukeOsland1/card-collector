"""Discord slash command implementations."""
import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import get_db
from db.crud import AuditLogCRUD, CardCRUD, CardInstanceCRUD, UserCRUD
from db.models import CardRarity, CardStatus

from .cdn import process_image_attachment, validate_image_attachment
from .embeds import (
    PaginationView,
    create_card_embed,
    create_card_instance_embed,
    create_error_embed,
    create_info_embed,
    create_success_embed,
    create_user_cards_embed,
)
from .permissions import check_permissions, get_permission_error_message

logger = logging.getLogger(__name__)


class CardCommands(commands.GroupCog, name="card"):
    """Card management commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="submit")
    @app_commands.describe(
        name="Card name (max 100 characters)",
        rarity="Card rarity level",
        image="Card image attachment (PNG, JPG, WebP, max 5MB)",
        description="Card description (optional, max 500 characters)",
        tags="Comma-separated tags (optional, e.g. 'dragon,fire,legendary')"
    )
    async def submit_card(
        self,
        interaction: discord.Interaction,
        name: str,
        rarity: CardRarity,
        image: discord.Attachment,
        description: Optional[str] = None,
        tags: Optional[str] = None
    ):
        """Submit a card for review."""
        await interaction.response.defer()

        try:
            # Validate input
            if len(name) > 100:
                embed = create_error_embed("Card name cannot exceed 100 characters.")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if description and len(description) > 500:
                embed = create_error_embed("Description cannot exceed 500 characters.")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Validate image
            is_valid, error_message = await validate_image_attachment(image)
            if not is_valid:
                embed = create_error_embed(error_message)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Process image
            image_url, thumb_url = await process_image_attachment(image, rarity, name.strip())

            # Parse tags
            tag_list = None
            if tags:
                tag_list = [tag.strip()[:50] for tag in tags.split(",") if tag.strip()]
                tag_list = tag_list[:10]  # Limit to 10 tags

            # Create card
            async for db in get_db():
                # Ensure user exists
                await UserCRUD.get_or_create(db, interaction.user.id)
                
                card = await CardCRUD.create(
                    db,
                    name=name.strip(),
                    description=description.strip() if description else None,
                    rarity=rarity,
                    image_url=image_url,
                    thumb_url=thumb_url,
                    tags=tag_list,
                    created_by_user_id=interaction.user.id,
                    status=CardStatus.SUBMITTED
                )

                # Log action
                await AuditLogCRUD.create(
                    db,
                    actor_user_id=interaction.user.id,
                    action="card_submitted",
                    target_type="card",
                    target_id=card.id,
                    meta={
                        "name": name,
                        "rarity": rarity.value,
                        "guild_id": interaction.guild_id
                    }
                )

            embed = create_success_embed(
                f"Card **{name}** has been submitted for review!\n"
                f"Card ID: `{card.id}`\n\n"
                f"A moderator will review your submission soon."
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error submitting card: {e}")
            embed = create_error_embed("An error occurred while submitting the card. Please try again.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="create")
    @app_commands.describe(
        name="Card name (max 100 characters)",
        rarity="Card rarity level",
        image="Card image attachment (PNG, JPG, WebP, max 5MB)",
        description="Card description (optional, max 500 characters)",
        tags="Comma-separated tags (optional)",
        max_supply="Maximum supply (optional, 0 for unlimited)"
    )
    async def create_card(
        self,
        interaction: discord.Interaction,
        name: str,
        rarity: CardRarity,
        image: discord.Attachment,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        max_supply: Optional[int] = None
    ):
        """Create and immediately approve a card (moderator only)."""
        await interaction.response.defer()

        try:
            # Check permissions
            async for db in get_db():
                has_permission = await check_permissions(interaction, db, require_mod=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_mod=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Validate input
                if len(name) > 100:
                    embed = create_error_embed("Card name cannot exceed 100 characters.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                if description and len(description) > 500:
                    embed = create_error_embed("Description cannot exceed 500 characters.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                if max_supply is not None and max_supply < 0:
                    embed = create_error_embed("Max supply cannot be negative.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Validate image
                is_valid, error_message = await validate_image_attachment(image)
                if not is_valid:
                    embed = create_error_embed(error_message)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Process image
                image_url, thumb_url = await process_image_attachment(image, rarity, name.strip())

                # Parse tags
                tag_list = None
                if tags:
                    tag_list = [tag.strip()[:50] for tag in tags.split(",") if tag.strip()]
                    tag_list = tag_list[:10]

                # Create card
                card = await CardCRUD.create(
                    db,
                    name=name.strip(),
                    description=description.strip() if description else None,
                    rarity=rarity,
                    image_url=image_url,
                    thumb_url=thumb_url,
                    tags=tag_list,
                    created_by_user_id=interaction.user.id,
                    status=CardStatus.APPROVED,
                    max_supply=max_supply if max_supply != 0 else None
                )
                
                # Auto-approve
                card.approved_by_user_id = interaction.user.id
                await db.commit()
                await db.refresh(card)

                # Log action
                await AuditLogCRUD.create(
                    db,
                    actor_user_id=interaction.user.id,
                    action="card_created",
                    target_type="card",
                    target_id=card.id,
                    meta={
                        "name": name,
                        "rarity": rarity.value,
                        "guild_id": interaction.guild_id
                    }
                )

            embed = create_success_embed(
                f"Card **{name}** has been created and approved!\n"
                f"Card ID: `{card.id}`"
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error creating card: {e}")
            embed = create_error_embed("An error occurred while creating the card.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="approve")
    @app_commands.describe(card_id="Card ID to approve")
    async def approve_card(self, interaction: discord.Interaction, card_id: str):
        """Approve a submitted card (moderator only)."""
        await interaction.response.defer()

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_mod=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_mod=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Get and approve card
                card = await CardCRUD.approve(db, card_id, interaction.user.id)
                if not card:
                    embed = create_error_embed("Card not found or already processed.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Log action
                await AuditLogCRUD.create(
                    db,
                    actor_user_id=interaction.user.id,
                    action="card_approved",
                    target_type="card",
                    target_id=card.id,
                    meta={
                        "name": card.name,
                        "guild_id": interaction.guild_id
                    }
                )

            embed = create_success_embed(f"Card **{card.name}** has been approved!")
            
            # Try to notify the card creator
            try:
                creator = self.bot.get_user(card.created_by_user_id)
                if creator:
                    notify_embed = create_success_embed(
                        f"Your card **{card.name}** has been approved by {interaction.user.mention}!"
                    )
                    await creator.send(embed=notify_embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error approving card: {e}")
            embed = create_error_embed("An error occurred while approving the card.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="reject")
    @app_commands.describe(
        card_id="Card ID to reject",
        reason="Reason for rejection (optional)"
    )
    async def reject_card(
        self,
        interaction: discord.Interaction,
        card_id: str,
        reason: Optional[str] = None
    ):
        """Reject a submitted card (moderator only)."""
        await interaction.response.defer()

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_mod=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_mod=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Get and reject card
                card = await CardCRUD.reject(db, card_id)
                if not card:
                    embed = create_error_embed("Card not found or already processed.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Log action
                await AuditLogCRUD.create(
                    db,
                    actor_user_id=interaction.user.id,
                    action="card_rejected",
                    target_type="card",
                    target_id=card.id,
                    meta={
                        "name": card.name,
                        "reason": reason,
                        "guild_id": interaction.guild_id
                    }
                )

            message = f"Card **{card.name}** has been rejected."
            if reason:
                message += f"\n**Reason:** {reason}"
            
            embed = create_info_embed("Card Rejected", message)
            
            # Try to notify the card creator
            try:
                creator = self.bot.get_user(card.created_by_user_id)
                if creator:
                    notify_embed = create_error_embed(
                        f"Your card **{card.name}** was rejected by {interaction.user.mention}."
                        + (f"\n**Reason:** {reason}" if reason else "")
                    )
                    await creator.send(embed=notify_embed)
            except discord.Forbidden:
                pass
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error rejecting card: {e}")
            embed = create_error_embed("An error occurred while rejecting the card.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="assign")
    @app_commands.describe(
        card_id="Card ID to assign",
        user="User to assign card to",
        expires_in_minutes="Card expires after this many minutes (optional)",
        note="Note for this assignment (optional, max 200 characters)"
    )
    async def assign_card(
        self,
        interaction: discord.Interaction,
        card_id: str,
        user: discord.Member,
        expires_in_minutes: Optional[int] = None,
        note: Optional[str] = None
    ):
        """Assign a card to a user (moderator only)."""
        await interaction.response.defer()

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_mod=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_mod=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Validate input
                if expires_in_minutes is not None and expires_in_minutes <= 0:
                    embed = create_error_embed("Expiry time must be positive.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                    
                if note and len(note) > 200:
                    embed = create_error_embed("Note cannot exceed 200 characters.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Get card
                card = await CardCRUD.get(db, card_id)
                if not card:
                    embed = create_error_embed("Card not found.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                if card.status != CardStatus.APPROVED:
                    embed = create_error_embed("Card must be approved before it can be assigned.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Check supply limit
                if card.max_supply is not None and card.current_supply >= card.max_supply:
                    embed = create_error_embed("Card has reached maximum supply.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Ensure target user exists in database
                await UserCRUD.get_or_create(db, user.id)

                # Create instance
                instance = await CardInstanceCRUD.create(
                    db,
                    card_id=card_id,
                    owner_user_id=user.id,
                    assigned_by_user_id=interaction.user.id,
                    expires_in_minutes=expires_in_minutes,
                    notes=note
                )

                # Log action
                await AuditLogCRUD.create(
                    db,
                    actor_user_id=interaction.user.id,
                    action="card_assigned",
                    target_type="card_instance",
                    target_id=instance.id,
                    meta={
                        "card_name": card.name,
                        "card_id": card_id,
                        "recipient_id": user.id,
                        "expires_in_minutes": expires_in_minutes,
                        "guild_id": interaction.guild_id
                    }
                )

            message = f"Card **{card.name}** has been assigned to {user.mention}!"
            if expires_in_minutes:
                hours = expires_in_minutes // 60
                minutes = expires_in_minutes % 60
                if hours > 0:
                    message += f"\n⏰ Expires in {hours}h {minutes}m"
                else:
                    message += f"\n⏰ Expires in {minutes}m"
            
            embed = create_success_embed(message)
            
            # Try to notify the recipient
            try:
                notify_embed = create_success_embed(
                    f"You received a new card: **{card.name}**!\n"
                    f"Assigned by: {interaction.user.mention}"
                    + (f"\nExpires in: {expires_in_minutes} minutes" if expires_in_minutes else "")
                    + (f"\nNote: {note}" if note else "")
                )
                await user.send(embed=notify_embed)
            except discord.Forbidden:
                pass
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error assigning card: {e}")
            embed = create_error_embed("An error occurred while assigning the card.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="remove")
    @app_commands.describe(instance_id="Card instance ID to remove")
    async def remove_instance(self, interaction: discord.Interaction, instance_id: str):
        """Remove a card instance (moderator only)."""
        await interaction.response.defer()

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_mod=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_mod=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Remove instance
                instance = await CardInstanceCRUD.remove(db, instance_id, interaction.user.id)
                if not instance:
                    embed = create_error_embed("Card instance not found or already removed.")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Log action
                await AuditLogCRUD.create(
                    db,
                    actor_user_id=interaction.user.id,
                    action="card_instance_removed",
                    target_type="card_instance",
                    target_id=instance.id,
                    meta={
                        "card_name": instance.card.name,
                        "owner_id": instance.owner_user_id,
                        "guild_id": interaction.guild_id
                    }
                )

            embed = create_success_embed(
                f"Card instance **{instance.card.name}** has been removed from "
                f"<@{instance.owner_user_id}>."
            )
            
            # Try to notify the owner
            try:
                owner = self.bot.get_user(instance.owner_user_id)
                if owner:
                    notify_embed = create_info_embed(
                        "Card Removed",
                        f"Your card **{instance.card.name}** was removed by {interaction.user.mention}."
                    )
                    await owner.send(embed=notify_embed)
            except discord.Forbidden:
                pass
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error removing card instance: {e}")
            embed = create_error_embed("An error occurred while removing the card instance.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="my")
    @app_commands.describe(
        active_only="Show only active cards (default: True)",
        search="Search card names/descriptions",
        rarity="Filter by rarity",
        tag="Filter by tag"
    )
    async def my_cards(
        self,
        interaction: discord.Interaction,
        active_only: bool = True,
        search: Optional[str] = None,
        rarity: Optional[CardRarity] = None,
        tag: Optional[str] = None
    ):
        """View your card collection."""
        await interaction.response.defer(ephemeral=True)

        try:
            async for db in get_db():
                instances = await CardInstanceCRUD.get_user_instances(
                    db,
                    interaction.user.id,
                    active_only=active_only,
                    search=search,
                    rarity=rarity,
                    tag=tag,
                    limit=50
                )

            if not instances:
                filter_text = []
                if active_only:
                    filter_text.append("active")
                if search:
                    filter_text.append(f"matching '{search}'")
                if rarity:
                    filter_text.append(f"rarity {rarity.value}")
                if tag:
                    filter_text.append(f"tagged '{tag}'")
                
                filter_str = " ".join(filter_text) if filter_text else ""
                message = f"You have no cards{' ' + filter_str if filter_str else ''}."
                embed = create_info_embed("Your Cards", message)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Create pagination if many cards
            cards_per_page = 10
            if len(instances) <= cards_per_page:
                embed = create_user_cards_embed(
                    instances,
                    user=interaction.user,
                    active_only=active_only
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embeds = []
                total_pages = (len(instances) + cards_per_page - 1) // cards_per_page
                
                for page in range(total_pages):
                    start_idx = page * cards_per_page
                    end_idx = start_idx + cards_per_page
                    page_instances = instances[start_idx:end_idx]
                    
                    embed = create_user_cards_embed(
                        page_instances,
                        user=interaction.user,
                        active_only=active_only,
                        page=page + 1,
                        total_pages=total_pages
                    )
                    embeds.append(embed)
                
                view = PaginationView(embeds)
                await interaction.followup.send(embed=embeds[0], view=view, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting user cards: {e}")
            embed = create_error_embed("An error occurred while fetching your cards.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="info")
    @app_commands.describe(id="Card ID or instance ID")
    async def card_info(self, interaction: discord.Interaction, id: str):
        """Get information about a card or card instance."""
        await interaction.response.defer(ephemeral=True)

        try:
            async for db in get_db():
                # Try to get as card instance first
                instance = await CardInstanceCRUD.get(db, id)
                if instance:
                    # Check if user owns this instance or is a mod
                    has_mod_permission = await check_permissions(interaction, db, require_mod=True)
                    if not has_mod_permission and instance.owner_user_id != interaction.user.id:
                        embed = create_error_embed("You can only view your own card instances.")
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        return
                    
                    embed = create_card_instance_embed(
                        instance,
                        show_owner=has_mod_permission,
                        show_notes=True
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Try to get as card
                card = await CardCRUD.get(db, id)
                if card:
                    embed = create_card_embed(card, show_supply=True)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

            embed = create_error_embed("Card or instance not found.")
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting card info: {e}")
            embed = create_error_embed("An error occurred while fetching card information.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="queue")
    async def review_queue(self, interaction: discord.Interaction):
        """View cards waiting for review (moderator only)."""
        await interaction.response.defer(ephemeral=True)

        try:
            async for db in get_db():
                # Check permissions
                has_permission = await check_permissions(interaction, db, require_mod=True)
                if not has_permission:
                    error_msg = await get_permission_error_message(interaction, require_mod=True)
                    embed = create_error_embed(error_msg)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Get submitted cards
                submitted_cards = await CardCRUD.get_all(
                    db,
                    status=CardStatus.SUBMITTED,
                    limit=20
                )

            if not submitted_cards:
                embed = create_info_embed("Review Queue", "No cards waiting for review.")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Create queue embed
            embed = discord.Embed(
                title="📋 Card Review Queue",
                description=f"**{len(submitted_cards)} cards** waiting for review:",
                color=0x3498db
            )

            for i, card in enumerate(submitted_cards[:10], 1):
                embed.add_field(
                    name=f"{i}. {card.name}",
                    value=f"**Rarity:** {card.rarity.value.title()}\n"
                          f"**ID:** `{card.id}`\n"
                          f"**Submitted by:** <@{card.created_by_user_id}>",
                    inline=False
                )

            if len(submitted_cards) > 10:
                embed.set_footer(text=f"... and {len(submitted_cards) - 10} more cards")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting review queue: {e}")
            embed = create_error_embed("An error occurred while fetching the review queue.")
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    """Setup function for the commands cog."""
    await bot.add_cog(CardCommands(bot))