"""SQLAlchemy models for the card collector bot."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    BIGINT,
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from .base import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type."""

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return str(value)


class CardRarity(PyEnum):
    """Card rarity levels."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class CardStatus(PyEnum):
    """Card approval status."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class Card(Base):
    """Card model representing collectible cards."""

    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(
        GUID, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    rarity: Mapped[CardRarity] = mapped_column(Enum(CardRarity), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    thumb_url: Mapped[Optional[str]] = mapped_column(String(500))
    tags: Mapped[Optional[str]] = mapped_column(Text)  # CSV format
    status: Mapped[CardStatus] = mapped_column(
        Enum(CardStatus), nullable=False, default=CardStatus.DRAFT
    )
    max_supply: Mapped[Optional[int]] = mapped_column(Integer)

    # User references (Discord user IDs)
    created_by_user_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    approved_by_user_id: Mapped[Optional[int]] = mapped_column(BIGINT)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    instances: Mapped[list["CardInstance"]] = relationship(
        "CardInstance", back_populates="card", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_cards_status_rarity", "status", "rarity"),
        Index("ix_cards_created_by", "created_by_user_id"),
    )

    @property
    def tag_list(self) -> list[str]:
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    @tag_list.setter
    def tag_list(self, tags: list[str]) -> None:
        """Set tags from a list."""
        self.tags = ",".join(tags) if tags else None

    @property
    def current_supply(self) -> int:
        """Get current supply count."""
        return len([i for i in self.instances if i.is_active])

    def __repr__(self) -> str:
        return f"<Card(id={self.id}, name={self.name}, rarity={self.rarity.value})>"


class CardInstance(Base):
    """Card instance model representing individual card ownership."""

    __tablename__ = "card_instances"

    id: Mapped[str] = mapped_column(
        GUID, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    card_id: Mapped[str] = mapped_column(GUID, ForeignKey("cards.id"), nullable=False)
    owner_user_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    assigned_by_user_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    removed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_by_user_id: Mapped[Optional[int]] = mapped_column(BIGINT)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    card: Mapped["Card"] = relationship("Card", back_populates="instances")

    # Indexes
    __table_args__ = (
        Index(
            "ix_card_instances_owner_expires_removed",
            "owner_user_id",
            "expires_at",
            "removed_at",
        ),
        Index("ix_card_instances_card_id", "card_id"),
        Index("ix_card_instances_expires_at", "expires_at"),
    )

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
