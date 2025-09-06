"""MongoDB models for the card collector bot using Beanie ODM."""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any
import uuid

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from pymongo import IndexModel


class CardRarity(str, PyEnum):
    """Card rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class CardStatus(str, PyEnum):
    """Card approval status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class Card(Document):
    """Card document representing collectible cards."""
    
    # Use string ID for consistency with current system
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    rarity: CardRarity
    image_url: Optional[str] = Field(None, max_length=500)
    thumb_url: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(default_factory=list)  # Direct list instead of CSV
    status: CardStatus = Field(default=CardStatus.DRAFT)
    max_supply: Optional[int] = None
    
    # User references (Discord user IDs)
    created_by_user_id: int
    approved_by_user_id: Optional[int] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    
    # MongoDB-specific configuration
    class Settings:
        name = "cards"
        indexes = [
            IndexModel([("status", 1), ("rarity", 1)]),
            IndexModel([("created_by_user_id", 1)]),
            IndexModel([("name", "text"), ("description", "text"), ("tags", "text")]),
            IndexModel([("created_at", -1)]),
        ]
    
    @property
    def tag_list(self) -> List[str]:
        """Get tags as a list (already a list in MongoDB)."""
        return self.tags
    
    @tag_list.setter
    def tag_list(self, tags: List[str]) -> None:
        """Set tags from a list."""
        self.tags = tags or []
    
    def __repr__(self) -> str:
        return f"<Card(id={self.id}, name={self.name}, rarity={self.rarity.value})>"


class CardInstance(Document):
    """Card instance document representing individual card ownership."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    card_id: str  # Reference to Card document
    owner_user_id: int
    assigned_by_user_id: int
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    removed_at: Optional[datetime] = None
    revoked_by_user_id: Optional[int] = None
    is_locked: bool = Field(default=False)
    notes: Optional[str] = None
    
    class Settings:
        name = "card_instances"
        indexes = [
            IndexModel([("owner_user_id", 1), ("expires_at", 1), ("removed_at", 1)]),
            IndexModel([("card_id", 1)]),
            IndexModel([("expires_at", 1)]),
            IndexModel([("assigned_at", -1)]),
        ]
    
    @property
    def is_active(self) -> bool:
        """Check if the card instance is currently active."""
        now = datetime.utcnow()
        return (
            self.removed_at is None
            and (self.expires_at is None or self.expires_at > now)
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if the card instance is expired but not removed."""
        if self.removed_at is not None:
            return False
        if self.expires_at is None:
            return False
        return self.expires_at <= datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<CardInstance(id={self.id}, card_id={self.card_id}, owner={self.owner_user_id})>"


class User(Document):
    """User document for Discord users."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    discord_id: Indexed(int, unique=True)  # Beanie indexed field
    username: Optional[str] = Field(None, max_length=255)
    discriminator: Optional[str] = Field(None, max_length=10)
    avatar: Optional[str] = Field(None, max_length=255)
    global_name: Optional[str] = Field(None, max_length=255)
    
    # Activity tracking
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_activity: Optional[datetime] = None
    
    # Preferences
    timezone: Optional[str] = Field(None, max_length=50)
    notification_preferences: Dict[str, Any] = Field(default_factory=dict)
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel([("discord_id", 1)], unique=True),
            IndexModel([("username", 1)]),
            IndexModel([("last_activity", -1)]),
        ]
    
    def __repr__(self) -> str:
        return f"<User(discord_id={self.discord_id}, username={self.username})>"


class GuildConfig(Document):
    """Guild configuration document."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    guild_id: Indexed(int, unique=True)  # Beanie indexed field
    guild_name: Optional[str] = Field(None, max_length=255)
    
    # Permission configuration
    admin_role_ids: List[int] = Field(default_factory=list)
    mod_role_ids: List[int] = Field(default_factory=list)
    admin_user_ids: List[int] = Field(default_factory=list)
    mod_user_ids: List[int] = Field(default_factory=list)
    
    # Channel configuration
    card_channel_id: Optional[int] = None
    log_channel_id: Optional[int] = None
    notification_channel_id: Optional[int] = None
    
    # Feature configuration
    auto_approve_cards: bool = Field(default=False)
    allow_card_submissions: bool = Field(default=True)
    max_user_submissions: int = Field(default=5)
    submission_cooldown_hours: int = Field(default=24)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "guild_configs"
        indexes = [
            IndexModel([("guild_id", 1)], unique=True),
            IndexModel([("created_at", -1)]),
        ]
    
    def __repr__(self) -> str:
        return f"<GuildConfig(guild_id={self.guild_id}, name={self.guild_name})>"


class AuditLog(Document):
    """Audit log document for tracking actions."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Action details
    actor_user_id: int
    action: str = Field(..., max_length=100)
    target_type: Optional[str] = Field(None, max_length=50)
    target_id: Optional[str] = Field(None, max_length=255)
    
    # Additional context
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "audit_logs"
        indexes = [
            IndexModel([("actor_user_id", 1), ("created_at", -1)]),
            IndexModel([("action", 1), ("created_at", -1)]),
            IndexModel([("target_type", 1), ("target_id", 1)]),
            IndexModel([("guild_id", 1), ("created_at", -1)]),
            IndexModel([("created_at", -1)]),  # Most recent first
        ]
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, actor={self.actor_user_id})>"


class CardSubmission(Document):
    """Card submission tracking document."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    card_id: str  # Reference to Card document
    submitter_id: int
    
    # Submission details
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    submission_message: Optional[str] = None
    
    # Review details
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    review_decision: Optional[str] = Field(None, max_length=20)  # approved, rejected
    review_notes: Optional[str] = None
    
    class Settings:
        name = "card_submissions"
        indexes = [
            IndexModel([("card_id", 1)]),
            IndexModel([("submitter_id", 1), ("submitted_at", -1)]),
            IndexModel([("review_decision", 1), ("submitted_at", -1)]),
            IndexModel([("submitted_at", -1)]),
        ]
    
    def __repr__(self) -> str:
        return f"<CardSubmission(id={self.id}, card_id={self.card_id}, status={self.review_decision})>"


# List all document models for easy import
__all__ = [
    "Card",
    "CardInstance", 
    "User",
    "GuildConfig",
    "AuditLog",
    "CardSubmission",
    "CardRarity",
    "CardStatus",
]