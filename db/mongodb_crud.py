"""MongoDB CRUD operations for the card collector bot using Beanie ODM."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId
from beanie.operators import In, And, Or, GTE, LTE, NE, Exists
from pymongo.errors import DuplicateKeyError

from .mongodb_models import (
    AuditLog,
    Card,
    CardInstance,
    CardRarity,
    CardStatus,
    GuildConfig,
    User,
    CardSubmission,
)

logger = logging.getLogger(__name__)


class MongoCardCRUD:
    """MongoDB CRUD operations for Card model."""
    
    @staticmethod
    async def create(
        name: str,
        description: Optional[str],
        rarity: CardRarity,
        created_by_user_id: int,
        image_url: Optional[str] = None,
        thumb_url: Optional[str] = None,
        tags: List[str] = None,
        status: CardStatus = CardStatus.DRAFT,
        max_supply: Optional[int] = None,
    ) -> Card:
        """Create a new card."""
        card = Card(
            name=name,
            description=description,
            rarity=rarity,
            image_url=image_url,
            thumb_url=thumb_url,
            tags=tags or [],
            status=status,
            max_supply=max_supply,
            created_by_user_id=created_by_user_id,
        )
        await card.insert()
        return card
    
    @staticmethod
    async def get_by_id(card_id: str) -> Optional[Card]:
        """Get card by ID."""
        return await Card.find_one(Card.id == card_id)
    
    @staticmethod
    async def get_all(
        limit: int = 100,
        skip: int = 0,
        status: Optional[CardStatus] = None,
        rarity: Optional[CardRarity] = None,
        created_by: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[Card]:
        """Get cards with optional filtering."""
        query = Card.find()
        
        # Apply filters
        conditions = []
        if status:
            conditions.append(Card.status == status)
        if rarity:
            conditions.append(Card.rarity == rarity)
        if created_by:
            conditions.append(Card.created_by_user_id == created_by)
        if search:
            # Text search across name, description, and tags
            conditions.append(
                Or(
                    Card.name.contains(search, ignore_case=True),
                    Card.description.contains(search, ignore_case=True),
                    In(search.lower(), Card.tags),
                )
            )
        
        if conditions:
            query = query.find(And(*conditions))
        
        return await query.skip(skip).limit(limit).sort(-Card.created_at).to_list()
    
    @staticmethod
    async def update(card_id: str, **kwargs) -> Optional[Card]:
        """Update card by ID."""
        card = await Card.find_one(Card.id == card_id)
        if not card:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(card, key):
                setattr(card, key, value)
        
        await card.save()
        return card
    
    @staticmethod
    async def delete(card_id: str) -> bool:
        """Delete card by ID."""
        card = await Card.find_one(Card.id == card_id)
        if card:
            await card.delete()
            return True
        return False
    
    @staticmethod
    async def approve(card_id: str, approved_by_user_id: int) -> Optional[Card]:
        """Approve a card."""
        return await MongoCardCRUD.update(
            card_id,
            status=CardStatus.APPROVED,
            approved_by_user_id=approved_by_user_id,
            approved_at=datetime.utcnow(),
        )
    
    @staticmethod
    async def reject(card_id: str) -> Optional[Card]:
        """Reject a card."""
        return await MongoCardCRUD.update(card_id, status=CardStatus.REJECTED)
    
    @staticmethod
    async def get_pending_approval() -> List[Card]:
        """Get cards pending approval."""
        return await Card.find(Card.status == CardStatus.SUBMITTED).to_list()


class MongoCardInstanceCRUD:
    """MongoDB CRUD operations for CardInstance model."""
    
    @staticmethod
    async def create(
        card_id: str,
        owner_user_id: int,
        assigned_by_user_id: int,
        expires_at: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> CardInstance:
        """Create a new card instance."""
        instance = CardInstance(
            card_id=card_id,
            owner_user_id=owner_user_id,
            assigned_by_user_id=assigned_by_user_id,
            expires_at=expires_at,
            notes=notes,
        )
        await instance.insert()
        return instance
    
    @staticmethod
    async def get_by_id(instance_id: str) -> Optional[CardInstance]:
        """Get card instance by ID."""
        return await CardInstance.find_one(CardInstance.id == instance_id)
    
    @staticmethod
    async def get_user_collection(
        user_id: int,
        active_only: bool = True,
        limit: int = 100,
        skip: int = 0,
    ) -> List[CardInstance]:
        """Get user's card collection."""
        query = CardInstance.find(CardInstance.owner_user_id == user_id)
        
        if active_only:
            now = datetime.utcnow()
            query = query.find(
                And(
                    CardInstance.removed_at == None,
                    Or(
                        CardInstance.expires_at == None,
                        CardInstance.expires_at > now,
                    ),
                )
            )
        
        return await query.skip(skip).limit(limit).sort(-CardInstance.assigned_at).to_list()
    
    @staticmethod
    async def get_by_card(card_id: str, active_only: bool = True) -> List[CardInstance]:
        """Get all instances of a specific card."""
        query = CardInstance.find(CardInstance.card_id == card_id)
        
        if active_only:
            now = datetime.utcnow()
            query = query.find(
                And(
                    CardInstance.removed_at == None,
                    Or(
                        CardInstance.expires_at == None,
                        CardInstance.expires_at > now,
                    ),
                )
            )
        
        return await query.to_list()
    
    @staticmethod
    async def remove_instance(
        instance_id: str,
        revoked_by_user_id: Optional[int] = None,
    ) -> Optional[CardInstance]:
        """Remove/revoke a card instance."""
        instance = await CardInstance.find_one(CardInstance.id == instance_id)
        if instance:
            instance.removed_at = datetime.utcnow()
            instance.revoked_by_user_id = revoked_by_user_id
            await instance.save()
        return instance
    
    @staticmethod
    async def get_expired_instances() -> List[CardInstance]:
        """Get instances that have expired but not been removed."""
        now = datetime.utcnow()
        return await CardInstance.find(
            And(
                CardInstance.expires_at <= now,
                CardInstance.removed_at == None,
            )
        ).to_list()


class MongoUserCRUD:
    """MongoDB CRUD operations for User model."""
    
    @staticmethod
    async def create_or_update(
        discord_id: int,
        username: Optional[str] = None,
        discriminator: Optional[str] = None,
        avatar: Optional[str] = None,
        global_name: Optional[str] = None,
    ) -> User:
        """Create new user or update existing one."""
        user = await User.find_one(User.discord_id == discord_id)
        
        if user:
            # Update existing user
            user.username = username
            user.discriminator = discriminator
            user.avatar = avatar
            user.global_name = global_name
            user.last_activity = datetime.utcnow()
            await user.save()
        else:
            # Create new user
            user = User(
                discord_id=discord_id,
                username=username,
                discriminator=discriminator,
                avatar=avatar,
                global_name=global_name,
                last_activity=datetime.utcnow(),
            )
            await user.insert()
        
        return user
    
    @staticmethod
    async def get_by_discord_id(discord_id: int) -> Optional[User]:
        """Get user by Discord ID."""
        return await User.find_one(User.discord_id == discord_id)
    
    @staticmethod
    async def get_or_create(db, discord_id: int) -> User:
        """Get or create user by Discord ID (compatible with SQL CRUD interface)."""
        user = await User.find_one(User.discord_id == discord_id)
        
        if not user:
            user = User(
                discord_id=discord_id,
                last_activity=datetime.utcnow(),
            )
            await user.insert()
            logger.info(f"Created new user: {discord_id}")
        
        return user
    
    @staticmethod
    async def get_by_id(user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await User.find_one(User.id == user_id)
    
    @staticmethod
    async def update_last_activity(db, discord_id: int) -> Optional[User]:
        """Update user's last activity timestamp."""
        user = await User.find_one(User.discord_id == discord_id)
        if user:
            user.last_activity = datetime.utcnow()
            await user.save()
        return user
    
    @staticmethod
    async def update_activity(discord_id: int) -> Optional[User]:
        """Update user's last activity."""
        user = await User.find_one(User.discord_id == discord_id)
        if user:
            user.last_activity = datetime.utcnow()
            await user.save()
        return user


class MongoGuildConfigCRUD:
    """MongoDB CRUD operations for GuildConfig model."""
    
    @staticmethod
    async def create_or_update(guild_id: int, **kwargs) -> GuildConfig:
        """Create new guild config or update existing one."""
        config = await GuildConfig.find_one(GuildConfig.guild_id == guild_id)
        
        if config:
            # Update existing config
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            config.updated_at = datetime.utcnow()
            await config.save()
        else:
            # Create new config
            config = GuildConfig(guild_id=guild_id, **kwargs)
            await config.insert()
        
        return config
    
    @staticmethod
    async def get_by_guild_id(guild_id: int) -> Optional[GuildConfig]:
        """Get guild config by guild ID."""
        return await GuildConfig.find_one(GuildConfig.guild_id == guild_id)
    
    @staticmethod
    async def delete_by_guild_id(guild_id: int) -> bool:
        """Delete guild config by guild ID."""
        config = await GuildConfig.find_one(GuildConfig.guild_id == guild_id)
        if config:
            await config.delete()
            return True
        return False


class MongoAuditLogCRUD:
    """MongoDB CRUD operations for AuditLog model."""
    
    @staticmethod
    async def create(
        actor_user_id: int,
        action: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        guild_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Create a new audit log entry."""
        log_entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            guild_id=guild_id,
            channel_id=channel_id,
            meta=meta or {},
        )
        await log_entry.insert()
        return log_entry
    
    @staticmethod
    async def get_recent(
        limit: int = 100,
        guild_id: Optional[int] = None,
        actor_user_id: Optional[int] = None,
        action: Optional[str] = None,
    ) -> List[AuditLog]:
        """Get recent audit log entries."""
        query = AuditLog.find()
        
        conditions = []
        if guild_id:
            conditions.append(AuditLog.guild_id == guild_id)
        if actor_user_id:
            conditions.append(AuditLog.actor_user_id == actor_user_id)
        if action:
            conditions.append(AuditLog.action == action)
        
        if conditions:
            query = query.find(And(*conditions))
        
        return await query.limit(limit).sort(-AuditLog.created_at).to_list()


# Export CRUD classes for easy import
__all__ = [
    "MongoCardCRUD",
    "MongoCardInstanceCRUD", 
    "MongoUserCRUD",
    "MongoGuildConfigCRUD",
    "MongoAuditLogCRUD",
]