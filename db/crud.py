"""Database CRUD operations for the card collector bot."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    AuditLog,
    Card,
    CardInstance,
    CardRarity,
    CardStatus,
    GuildConfig,
    User,
)

logger = logging.getLogger(__name__)


class BaseCRUD:
    """Base CRUD operations."""

    @classmethod
    async def get(cls, db: AsyncSession, id: str):
        """Get object by ID."""
        result = await db.execute(select(cls.model).where(cls.model.id == id))
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        """Create new object."""
        obj = cls.model(**kwargs)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    @classmethod
    async def update(cls, db: AsyncSession, id: str, **kwargs):
        """Update object by ID."""
        result = await db.execute(select(cls.model).where(cls.model.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            await db.commit()
            await db.refresh(obj)
        return obj

    @classmethod
    async def delete(cls, db: AsyncSession, id: str):
        """Delete object by ID."""
        result = await db.execute(select(cls.model).where(cls.model.id == id))
        obj = result.scalar_one_or_none()
        if obj:
            await db.delete(obj)
            await db.commit()
            return True
        return False


class UserCRUD(BaseCRUD):
    """User CRUD operations."""
    model = User

    @classmethod
    async def get_or_create(cls, db: AsyncSession, user_id: int) -> User:
        """Get or create user by Discord ID."""
        result = await db.execute(select(User).where(User.discord_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(discord_id=user_id)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Created new user: {user_id}")
        
        return user

    @classmethod
    async def get_by_discord_id(cls, db: AsyncSession, discord_id: int) -> Optional[User]:
        """Get user by Discord ID."""
        result = await db.execute(select(User).where(User.discord_id == discord_id))
        return result.scalar_one_or_none()

    @classmethod
    async def update_last_activity(cls, db: AsyncSession, discord_id: int):
        """Update user's last activity timestamp."""
        result = await db.execute(select(User).where(User.discord_id == discord_id))
        user = result.scalar_one_or_none()
        if user:
            user.last_activity = datetime.utcnow()
            await db.commit()

    @classmethod
    async def get_active_users(cls, db: AsyncSession, days: int = 30) -> List[User]:
        """Get users active within the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await db.execute(
            select(User)
            .where(User.last_activity >= cutoff_date)
            .order_by(desc(User.last_activity))
        )
        return result.scalars().all()


class CardCRUD(BaseCRUD):
    """Card CRUD operations."""
    model = Card

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        name: str,
        rarity: CardRarity,
        created_by_user_id: int,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        thumb_url: Optional[str] = None,
        tags: Optional[List[str]] = None,
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
            status=status,
            max_supply=max_supply,
            created_by_user_id=created_by_user_id,
        )
        
        if tags:
            card.tag_list = tags
        
        db.add(card)
        await db.commit()
        await db.refresh(card)
        return card

    @classmethod
    async def get_all(
        cls,
        db: AsyncSession,
        status: Optional[CardStatus] = None,
        rarity: Optional[CardRarity] = None,
        search: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Card]:
        """Get cards with filtering options."""
        query = select(Card).options(selectinload(Card.instances))
        
        # Apply filters
        if status:
            query = query.where(Card.status == status)
        
        if rarity:
            query = query.where(Card.rarity == rarity)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Card.name.ilike(search_term),
                    Card.description.ilike(search_term),
                )
            )
        
        if tag:
            query = query.where(Card.tags.ilike(f"%{tag}%"))
        
        query = query.order_by(desc(Card.created_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def approve(cls, db: AsyncSession, card_id: str, approved_by_user_id: int) -> Optional[Card]:
        """Approve a submitted card."""
        result = await db.execute(select(Card).where(Card.id == card_id))
        card = result.scalar_one_or_none()
        
        if card and card.status == CardStatus.SUBMITTED:
            card.status = CardStatus.APPROVED
            card.approved_by_user_id = approved_by_user_id
            card.approved_at = datetime.utcnow()
            await db.commit()
            await db.refresh(card)
            return card
        
        return None

    @classmethod
    async def reject(cls, db: AsyncSession, card_id: str) -> Optional[Card]:
        """Reject a submitted card."""
        result = await db.execute(select(Card).where(Card.id == card_id))
        card = result.scalar_one_or_none()
        
        if card and card.status == CardStatus.SUBMITTED:
            card.status = CardStatus.REJECTED
            await db.commit()
            await db.refresh(card)
            return card
        
        return None

    @classmethod
    async def get_by_creator(cls, db: AsyncSession, creator_id: int) -> List[Card]:
        """Get cards created by a specific user."""
        result = await db.execute(
            select(Card)
            .where(Card.created_by_user_id == creator_id)
            .order_by(desc(Card.created_at))
        )
        return result.scalars().all()

    @classmethod
    async def search(cls, db: AsyncSession, query: str, limit: int = 20) -> List[Card]:
        """Search cards by name, description, or tags."""
        search_term = f"%{query}%"
        result = await db.execute(
            select(Card)
            .where(
                and_(
                    Card.status == CardStatus.APPROVED,
                    or_(
                        Card.name.ilike(search_term),
                        Card.description.ilike(search_term),
                        Card.tags.ilike(search_term),
                    ),
                )
            )
            .order_by(desc(Card.created_at))
            .limit(limit)
        )
        return result.scalars().all()


class CardInstanceCRUD(BaseCRUD):
    """Card instance CRUD operations."""
    model = CardInstance

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        card_id: str,
        owner_user_id: int,
        assigned_by_user_id: int,
        expires_in_minutes: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> CardInstance:
        """Create a new card instance."""
        expires_at = None
        if expires_in_minutes:
            expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        instance = CardInstance(
            card_id=card_id,
            owner_user_id=owner_user_id,
            assigned_by_user_id=assigned_by_user_id,
            expires_at=expires_at,
            notes=notes,
        )
        
        db.add(instance)
        await db.commit()
        await db.refresh(instance, ["card"])
        return instance

    @classmethod
    async def get_user_instances(
        cls,
        db: AsyncSession,
        user_id: int,
        active_only: bool = True,
        search: Optional[str] = None,
        rarity: Optional[CardRarity] = None,
        tag: Optional[str] = None,
        limit: int = 50,
    ) -> List[CardInstance]:
        """Get card instances for a user with filtering."""
        query = (
            select(CardInstance)
            .options(selectinload(CardInstance.card))
            .where(CardInstance.owner_user_id == user_id)
        )
        
        if active_only:
            now = datetime.utcnow()
            query = query.where(
                and_(
                    CardInstance.removed_at.is_(None),
                    or_(
                        CardInstance.expires_at.is_(None),
                        CardInstance.expires_at > now,
                    ),
                )
            )
        
        if search:
            search_term = f"%{search}%"
            query = query.join(Card).where(
                or_(
                    Card.name.ilike(search_term),
                    Card.description.ilike(search_term),
                )
            )
        
        if rarity:
            query = query.join(Card).where(Card.rarity == rarity)
        
        if tag:
            query = query.join(Card).where(Card.tags.ilike(f"%{tag}%"))
        
        query = query.order_by(desc(CardInstance.assigned_at)).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def remove(cls, db: AsyncSession, instance_id: str, removed_by_user_id: int) -> Optional[CardInstance]:
        """Remove a card instance."""
        result = await db.execute(
            select(CardInstance)
            .options(selectinload(CardInstance.card))
            .where(CardInstance.id == instance_id)
        )
        instance = result.scalar_one_or_none()
        
        if instance and instance.removed_at is None:
            instance.removed_at = datetime.utcnow()
            instance.revoked_by_user_id = removed_by_user_id
            await db.commit()
            await db.refresh(instance)
            return instance
        
        return None

    @classmethod
    async def get_expired_instances(cls, db: AsyncSession) -> List[CardInstance]:
        """Get all expired but not removed instances."""
        now = datetime.utcnow()
        result = await db.execute(
            select(CardInstance)
            .options(selectinload(CardInstance.card))
            .where(
                and_(
                    CardInstance.expires_at <= now,
                    CardInstance.removed_at.is_(None),
                )
            )
        )
        return result.scalars().all()

    @classmethod
    async def lock_instance(cls, db: AsyncSession, instance_id: str, locked: bool = True) -> Optional[CardInstance]:
        """Lock or unlock a card instance."""
        result = await db.execute(select(CardInstance).where(CardInstance.id == instance_id))
        instance = result.scalar_one_or_none()
        
        if instance:
            instance.is_locked = locked
            await db.commit()
            await db.refresh(instance)
            return instance
        
        return None

    @classmethod
    async def get_card_leaderboard(
        cls, db: AsyncSession, limit: int = 10, active_only: bool = True
    ) -> List[tuple]:
        """Get card collection leaderboard."""
        query = select(CardInstance.owner_user_id, func.count(CardInstance.id).label("count"))
        
        if active_only:
            now = datetime.utcnow()
            query = query.where(
                and_(
                    CardInstance.removed_at.is_(None),
                    or_(
                        CardInstance.expires_at.is_(None),
                        CardInstance.expires_at > now,
                    ),
                )
            )
        
        query = (
            query.group_by(CardInstance.owner_user_id)
            .order_by(desc("count"))
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.all()


class GuildConfigCRUD(BaseCRUD):
    """Guild configuration CRUD operations."""
    model = GuildConfig

    @classmethod
    async def get_or_create(cls, db: AsyncSession, guild_id: int) -> GuildConfig:
        """Get or create guild configuration."""
        result = await db.execute(select(GuildConfig).where(GuildConfig.guild_id == guild_id))
        config = result.scalar_one_or_none()
        
        if not config:
            config = GuildConfig(guild_id=guild_id)
            db.add(config)
            await db.commit()
            await db.refresh(config)
            logger.info(f"Created guild config for: {guild_id}")
        
        return config

    @classmethod
    async def update_config(
        cls,
        db: AsyncSession,
        guild_id: int,
        **kwargs,
    ) -> Optional[GuildConfig]:
        """Update guild configuration."""
        config = await cls.get_or_create(db, guild_id)
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        await db.commit()
        await db.refresh(config)
        return config


class AuditLogCRUD(BaseCRUD):
    """Audit log CRUD operations."""
    model = AuditLog

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        actor_user_id: int,
        action: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        log_entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            meta=meta or {},
        )
        
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        return log_entry

    @classmethod
    async def get_user_actions(
        cls,
        db: AsyncSession,
        user_id: int,
        limit: int = 50,
        actions: Optional[List[str]] = None,
    ) -> List[AuditLog]:
        """Get audit logs for a specific user."""
        query = select(AuditLog).where(AuditLog.actor_user_id == user_id)
        
        if actions:
            query = query.where(AuditLog.action.in_(actions))
        
        query = query.order_by(desc(AuditLog.created_at)).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_recent_actions(
        cls,
        db: AsyncSession,
        limit: int = 100,
        action: Optional[str] = None,
        days: int = 7,
    ) -> List[AuditLog]:
        """Get recent audit logs."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = select(AuditLog).where(AuditLog.created_at >= cutoff_date)
        
        if action:
            query = query.where(AuditLog.action == action)
        
        query = query.order_by(desc(AuditLog.created_at)).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_card_history(cls, db: AsyncSession, card_id: str) -> List[AuditLog]:
        """Get audit history for a specific card."""
        result = await db.execute(
            select(AuditLog)
            .where(
                and_(
                    AuditLog.target_type == "card",
                    AuditLog.target_id == card_id,
                )
            )
            .order_by(desc(AuditLog.created_at))
        )
        return result.scalars().all()

    @classmethod
    async def cleanup_old_logs(cls, db: AsyncSession, days: int = 90):
        """Clean up old audit logs."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await db.execute(
            select(func.count(AuditLog.id)).where(AuditLog.created_at < cutoff_date)
        )
        count = result.scalar()
        
        if count > 0:
            await db.execute(AuditLog.__table__.delete().where(AuditLog.created_at < cutoff_date))
            await db.commit()
            logger.info(f"Cleaned up {count} old audit log entries")
        
        return count