"""Discord embed builders and pagination for card collector bot."""
import discord
from datetime import datetime
from typing import List, Optional

from db.models import Card, CardInstance, CardRarity, CardStatus


class PaginationView(discord.ui.View):
    """Pagination view for navigating through multiple embeds."""
    
    def __init__(self, embeds: List[discord.Embed], timeout: float = 300):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.total_pages = len(embeds)
        
        # Disable buttons if only one page
        if self.total_pages <= 1:
            self.clear_items()
    
    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.primary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to first page."""
        self.current_page = 0
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous page."""
        self.current_page = (self.current_page - 1) % self.total_pages
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to next page."""
        self.current_page = (self.current_page + 1) % self.total_pages
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.primary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to last page."""
        self.current_page = self.total_pages - 1
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
    
    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.danger)
    async def delete_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Delete the paginated message."""
        await interaction.response.defer()
        await interaction.delete_original_response()


def get_rarity_color(rarity: CardRarity) -> int:
    """Get Discord color code for card rarity."""
    colors = {
        CardRarity.COMMON: 0x95a5a6,      # Gray
        CardRarity.UNCOMMON: 0x2ecc71,    # Green
        CardRarity.RARE: 0x3498db,        # Blue
        CardRarity.EPIC: 0x9b59b6,        # Purple
        CardRarity.LEGENDARY: 0xf39c12,   # Gold
    }
    return colors.get(rarity, 0x7289da)


def get_rarity_emoji(rarity: CardRarity) -> str:
    """Get emoji for card rarity."""
    emojis = {
        CardRarity.COMMON: "⚪",
        CardRarity.UNCOMMON: "🟢",
        CardRarity.RARE: "🔵",
        CardRarity.EPIC: "🟣",
        CardRarity.LEGENDARY: "🟡",
    }
    return emojis.get(rarity, "⚪")


def get_status_emoji(status: CardStatus) -> str:
    """Get emoji for card status."""
    emojis = {
        CardStatus.DRAFT: "📝",
        CardStatus.SUBMITTED: "⏳",
        CardStatus.APPROVED: "✅",
        CardStatus.REJECTED: "❌",
        CardStatus.ARCHIVED: "🗄️",
    }
    return emojis.get(status, "📝")


def create_success_embed(message: str) -> discord.Embed:
    """Create a success embed with green color."""
    embed = discord.Embed(
        title="✅ Success",
        description=message,
        color=0x2ecc71
    )
    return embed


def create_error_embed(message: str) -> discord.Embed:
    """Create an error embed with red color."""
    embed = discord.Embed(
        title="❌ Error",
        description=message,
        color=0xe74c3c
    )
    return embed


def create_info_embed(title: str, message: str) -> discord.Embed:
    """Create an info embed with blue color."""
    embed = discord.Embed(
        title=f"ℹ️ {title}",
        description=message,
        color=0x3498db
    )
    return embed


def create_warning_embed(message: str) -> discord.Embed:
    """Create a warning embed with yellow color."""
    embed = discord.Embed(
        title="⚠️ Warning",
        description=message,
        color=0xf39c12
    )
    return embed


def create_card_embed(
    card: Card,
    show_supply: bool = False,
    show_creator: bool = False,
    show_status: bool = False
) -> discord.Embed:
    """Create an embed for displaying card information."""
    rarity_emoji = get_rarity_emoji(card.rarity)
    color = get_rarity_color(card.rarity)
    
    embed = discord.Embed(
        title=f"{rarity_emoji} {card.name}",
        color=color
    )
    
    # Add description if available
    if card.description:
        embed.description = card.description
    
    # Add card image
    if card.image_url:
        embed.set_image(url=card.image_url)
    elif card.thumb_url:
        embed.set_image(url=card.thumb_url)
    
    # Add fields
    embed.add_field(
        name="Rarity",
        value=f"{rarity_emoji} {card.rarity.value.title()}",
        inline=True
    )
    
    embed.add_field(
        name="Card ID",
        value=f"`{card.id}`",
        inline=True
    )
    
    if show_status:
        status_emoji = get_status_emoji(card.status)
        embed.add_field(
            name="Status",
            value=f"{status_emoji} {card.status.value.title()}",
            inline=True
        )
    
    if show_supply:
        if card.max_supply is not None:
            supply_text = f"{card.current_supply}/{card.max_supply}"
        else:
            supply_text = f"{card.current_supply}/∞"
        
        embed.add_field(
            name="Supply",
            value=supply_text,
            inline=True
        )
    
    if show_creator and card.created_by_user_id:
        embed.add_field(
            name="Created by",
            value=f"<@{card.created_by_user_id}>",
            inline=True
        )
    
    # Add tags if available
    if card.tag_list:
        tags_text = ", ".join([f"`{tag}`" for tag in card.tag_list[:5]])
        if len(card.tag_list) > 5:
            tags_text += f" +{len(card.tag_list) - 5} more"
        
        embed.add_field(
            name="Tags",
            value=tags_text,
            inline=False
        )
    
    # Add timestamp
    if card.created_at:
        embed.timestamp = card.created_at
        embed.set_footer(text="Created")
    
    return embed


def create_card_instance_embed(
    instance: CardInstance,
    show_owner: bool = False,
    show_notes: bool = False,
    show_timestamps: bool = True
) -> discord.Embed:
    """Create an embed for displaying card instance information."""
    card = instance.card
    rarity_emoji = get_rarity_emoji(card.rarity)
    color = get_rarity_color(card.rarity)
    
    title = f"{rarity_emoji} {card.name}"
    if instance.is_locked:
        title += " 🔒"
    
    embed = discord.Embed(
        title=title,
        color=color
    )
    
    # Add description if available
    if card.description:
        embed.description = card.description
    
    # Add card image
    if card.thumb_url:
        embed.set_thumbnail(url=card.thumb_url)
    elif card.image_url:
        embed.set_thumbnail(url=card.image_url)
    
    # Add fields
    embed.add_field(
        name="Rarity",
        value=f"{rarity_emoji} {card.rarity.value.title()}",
        inline=True
    )
    
    embed.add_field(
        name="Instance ID",
        value=f"`{instance.id}`",
        inline=True
    )
    
    embed.add_field(
        name="Card ID",
        value=f"`{card.id}`",
        inline=True
    )
    
    if show_owner:
        embed.add_field(
            name="Owner",
            value=f"<@{instance.owner_user_id}>",
            inline=True
        )
    
    # Add status information
    status_parts = []
    if instance.is_active:
        if instance.expires_at:
            if instance.is_expired:
                status_parts.append("⏰ Expired")
            else:
                expires_text = discord.utils.format_dt(instance.expires_at, style='R')
                status_parts.append(f"⏰ Expires {expires_text}")
        else:
            status_parts.append("✅ Active")
    else:
        status_parts.append("❌ Inactive")
    
    if instance.is_locked:
        status_parts.append("🔒 Locked")
    
    embed.add_field(
        name="Status",
        value=" • ".join(status_parts),
        inline=False
    )
    
    # Add notes if available and requested
    if show_notes and instance.notes:
        embed.add_field(
            name="Notes",
            value=instance.notes,
            inline=False
        )
    
    # Add timestamps
    if show_timestamps:
        embed.add_field(
            name="Assigned",
            value=discord.utils.format_dt(instance.assigned_at, style='f'),
            inline=True
        )
        
        if instance.expires_at:
            embed.add_field(
                name="Expires",
                value=discord.utils.format_dt(instance.expires_at, style='f'),
                inline=True
            )
        
        if instance.removed_at:
            embed.add_field(
                name="Removed",
                value=discord.utils.format_dt(instance.removed_at, style='f'),
                inline=True
            )
    
    return embed


def create_user_cards_embed(
    instances: List[CardInstance],
    user: discord.User,
    active_only: bool = True,
    page: Optional[int] = None,
    total_pages: Optional[int] = None
) -> discord.Embed:
    """Create an embed for displaying a user's card collection."""
    title = f"🎴 {user.display_name}'s Cards"
    if page and total_pages:
        title += f" (Page {page}/{total_pages})"
    
    embed = discord.Embed(
        title=title,
        color=0x7289da
    )
    
    if user.avatar:
        embed.set_thumbnail(url=user.avatar.url)
    
    if not instances:
        embed.description = "No cards found."
        return embed
    
    # Group by rarity for better organization
    rarity_groups = {}
    for instance in instances:
        rarity = instance.card.rarity
        if rarity not in rarity_groups:
            rarity_groups[rarity] = []
        rarity_groups[rarity].append(instance)
    
    # Sort rarities by value (common to legendary)
    rarity_order = [
        CardRarity.COMMON,
        CardRarity.UNCOMMON,
        CardRarity.RARE,
        CardRarity.EPIC,
        CardRarity.LEGENDARY
    ]
    
    for rarity in rarity_order:
        if rarity not in rarity_groups:
            continue
        
        instances_in_rarity = rarity_groups[rarity]
        rarity_emoji = get_rarity_emoji(rarity)
        
        cards_text = []
        for instance in instances_in_rarity:
            card_name = instance.card.name
            
            # Add status indicators
            indicators = []
            if instance.is_expired:
                indicators.append("⏰")
            if instance.is_locked:
                indicators.append("🔒")
            if not instance.is_active:
                indicators.append("❌")
            
            indicator_str = "".join(indicators)
            if indicator_str:
                card_name += f" {indicator_str}"
            
            # Add instance ID for reference
            cards_text.append(f"`{instance.id[:8]}` {card_name}")
        
        field_value = "\n".join(cards_text)
        if len(field_value) > 1024:  # Discord field limit
            field_value = field_value[:1020] + "..."
        
        embed.add_field(
            name=f"{rarity_emoji} {rarity.value.title()} ({len(instances_in_rarity)})",
            value=field_value,
            inline=False
        )
    
    # Add footer with legend
    footer_text = "Legend: ⏰ = Expired, 🔒 = Locked, ❌ = Inactive"
    if active_only:
        footer_text += " | Showing active cards only"
    
    embed.set_footer(text=footer_text)
    
    return embed


def create_leaderboard_embed(
    leaderboard_data: List[tuple],
    title: str = "🏆 Leaderboard",
    page: Optional[int] = None,
    total_pages: Optional[int] = None
) -> discord.Embed:
    """Create an embed for displaying leaderboard information."""
    embed_title = title
    if page and total_pages:
        embed_title += f" (Page {page}/{total_pages})"
    
    embed = discord.Embed(
        title=embed_title,
        color=0xf1c40f
    )
    
    if not leaderboard_data:
        embed.description = "No data available."
        return embed
    
    # Add leaderboard entries
    leaderboard_text = []
    for rank, (user_id, count) in enumerate(leaderboard_data, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
        leaderboard_text.append(f"{medal} <@{user_id}> - {count} cards")
    
    embed.description = "\n".join(leaderboard_text)
    
    return embed