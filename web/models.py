"""Pydantic models for API requests and responses."""
from datetime import datetime
from typing import Dict, Generic, List, Optional, TypeVar, Any

from pydantic import BaseModel, Field, field_validator

from db.models import CardRarity, CardStatus


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    items: List[T]
    total: int
    has_more: bool
    offset: int
    limit: int


# Card models
class CardBase(BaseModel):
    """Base card model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    rarity: CardRarity
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    tags: Optional[List[str]] = None
    max_supply: Optional[int] = Field(None, ge=1)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            # Limit to 10 tags, each max 50 characters
            v = v[:10]
            v = [tag.strip()[:50] for tag in v if tag.strip()]
        return v


class CardCreate(CardBase):
    """Model for creating a new card."""
    auto_approve: bool = False


class CardUpdate(BaseModel):
    """Model for updating an existing card."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    rarity: Optional[CardRarity] = None
    image_url: Optional[str] = None
    thumb_url: Optional[str] = None
    tags: Optional[List[str]] = None
    max_supply: Optional[int] = Field(None, ge=1)
    status: Optional[CardStatus] = None

    @validator("tags")
    def validate_tags(cls, v):
        if v is not None:
            v = v[:10]
            v = [tag.strip()[:50] for tag in v if tag.strip()]
        return v


class CardResponse(BaseModel):
    """Model for card API responses."""
    id: str
    name: str
    description: Optional[str]
    rarity: CardRarity
    image_url: Optional[str]
    thumb_url: Optional[str]
    tags: List[str] = []
    status: CardStatus
    max_supply: Optional[int]
    current_supply: int
    created_by_user_id: int
    approved_by_user_id: Optional[int]
    created_at: datetime
    approved_at: Optional[datetime]

    model_config = {"from_attributes": True}
        
    @classmethod
    def from_orm(cls, card):
        """Create response from ORM object."""
        return cls.model_validate({
            "id": card.id,
            "name": card.name,
            "description": card.description,
            "rarity": card.rarity,
            "image_url": card.image_url,
            "thumb_url": card.thumb_url,
            "tags": card.tag_list,
            "status": card.status,
            "max_supply": card.max_supply,
            "current_supply": card.current_supply,
            "created_by_user_id": card.created_by_user_id,
            "approved_by_user_id": card.approved_by_user_id,
            "created_at": card.created_at,
            "approved_at": card.approved_at,
        })


# Card instance models
class CardInstanceCreate(BaseModel):
    """Model for creating a card instance."""
    card_id: str
    owner_user_id: int
    expires_in_minutes: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=200)


class CardInstanceResponse(BaseModel):
    """Model for card instance API responses."""
    id: str
    card_id: str
    card: Optional[CardResponse] = None
    owner_user_id: int
    assigned_by_user_id: int
    assigned_at: datetime
    expires_at: Optional[datetime]
    removed_at: Optional[datetime]
    revoked_by_user_id: Optional[int]
    is_locked: bool
    notes: Optional[str]
    is_active: bool
    is_expired: bool

    model_config = {"from_attributes": True}
        
    @classmethod
    def from_orm(cls, instance):
        """Create response from ORM object."""
        card_response = None
        if hasattr(instance, 'card') and instance.card:
            card_response = CardResponse.from_orm(instance.card)
            
        return cls.model_validate({
            "id": instance.id,
            "card_id": instance.card_id,
            "card": card_response,
            "owner_user_id": instance.owner_user_id,
            "assigned_by_user_id": instance.assigned_by_user_id,
            "assigned_at": instance.assigned_at,
            "expires_at": instance.expires_at,
            "removed_at": instance.removed_at,
            "revoked_by_user_id": instance.revoked_by_user_id,
            "is_locked": instance.is_locked,
            "notes": instance.notes,
            "is_active": instance.is_active,
            "is_expired": instance.is_expired,
        })


# User models
class UserResponse(BaseModel):
    """Model for user API responses."""
    discord_id: int
    username: str
    is_moderator: bool = False
    is_admin: bool = False
    card_count: int = 0


# Guild configuration models
class GuildConfigResponse(BaseModel):
    """Model for guild configuration responses."""
    guild_id: int
    admin_role_ids: List[int] = []
    mod_role_ids: List[int] = []
    admin_user_ids: List[int] = []
    mod_user_ids: List[int] = []
    card_channel_id: Optional[int] = None
    log_channel_id: Optional[int] = None
    auto_approve_cards: bool = False
    max_user_submissions: int = 5
    submission_cooldown_hours: int = 24

    model_config = {"from_attributes": True}
        
    @classmethod
    def from_orm(cls, config):
        """Create response from ORM object."""
        return cls.model_validate({
            "guild_id": config.guild_id,
            "admin_role_ids": config.admin_role_ids or [],
            "mod_role_ids": config.mod_role_ids or [],
            "admin_user_ids": config.admin_user_ids or [],
            "mod_user_ids": config.mod_user_ids or [],
            "card_channel_id": config.card_channel_id,
            "log_channel_id": config.log_channel_id,
            "auto_approve_cards": config.auto_approve_cards,
            "max_user_submissions": config.max_user_submissions,
            "submission_cooldown_hours": config.submission_cooldown_hours,
        })


# Audit log models
class AuditLogResponse(BaseModel):
    """Model for audit log responses."""
    id: str
    actor_user_id: int
    action: str
    target_type: Optional[str]
    target_id: Optional[str]
    meta: Dict[str, Any] = {}
    created_at: datetime

    model_config = {"from_attributes": True}
        
    @classmethod
    def from_orm(cls, log):
        """Create response from ORM object."""
        return cls.model_validate({
            "id": log.id,
            "actor_user_id": log.actor_user_id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "meta": log.meta or {},
            "created_at": log.created_at,
        })


# Authentication models
class DiscordUser(BaseModel):
    """Discord user information from OAuth."""
    id: str
    username: str
    discriminator: str
    avatar: Optional[str]
    global_name: Optional[str]


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Error models
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""
    error: str = "validation_error"
    message: str
    details: List[Dict[str, Any]]


# Upload models
class ImageUploadResponse(BaseModel):
    """Image upload response model."""
    image_url: str
    thumb_url: str
    file_size: int
    dimensions: tuple[int, int]


# Statistics models
class CardStats(BaseModel):
    """Card statistics model."""
    total_cards: int
    approved_cards: int
    submitted_cards: int
    rejected_cards: int
    rarity_distribution: Dict[str, int]


class UserStats(BaseModel):
    """User statistics model."""
    user_id: int
    total_cards: int
    rarity_breakdown: Dict[str, int]
    most_recent_card: Optional[datetime]
    join_date: Optional[datetime]


class SystemStats(BaseModel):
    """System statistics model."""
    total_cards: int
    total_instances: int
    total_users: int
    active_users_last_30_days: int
    top_rarities: List[tuple[str, int]]
    recent_activity: int


# Leaderboard models
class LeaderboardEntry(BaseModel):
    """Leaderboard entry model."""
    rank: int
    user_id: int
    username: Optional[str] = None
    card_count: int
    percentage: float


class LeaderboardResponse(BaseModel):
    """Leaderboard response model."""
    leaderboard: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    total_users: int
    last_updated: datetime


# Search models
class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    results: List[CardResponse]
    count: int
    total_found: int
    suggestions: List[str] = []


# Bulk operation models
class BulkCardOperation(BaseModel):
    """Bulk card operation model."""
    card_ids: List[str] = Field(..., min_items=1, max_items=100)
    action: str = Field(..., pattern="^(approve|reject|archive)$")
    reason: Optional[str] = None


class BulkOperationResponse(BaseModel):
    """Bulk operation response model."""
    success_count: int
    failed_count: int
    errors: List[Dict[str, str]] = []
    processed_ids: List[str]


# Import/Export models
class CardExportFormat(BaseModel):
    """Card export format options."""
    format: str = Field(..., pattern="^(json|csv|xlsx)$")
    include_instances: bool = False
    include_inactive: bool = False
    filters: Optional[Dict[str, Any]] = None


class ExportResponse(BaseModel):
    """Export response model."""
    download_url: str
    expires_at: datetime
    file_size: int
    record_count: int


# Webhook models
class WebhookEvent(BaseModel):
    """Webhook event model."""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    guild_id: Optional[int] = None


# Rate limiting models  
class RateLimitInfo(BaseModel):
    """Rate limit information."""
    limit: int
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None