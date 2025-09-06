"""FastAPI API endpoints for card collector."""
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db_session
from db.crud import AuditLogCRUD, CardCRUD, CardInstanceCRUD, GuildConfigCRUD, UserCRUD
from db.models import Card, CardInstance, CardRarity, CardStatus

from .models import (
    CardCreate,
    CardSubmit,
    CardResponse,
    CardInstanceResponse,
    CardUpdate,
    UserResponse,
    PaginatedResponse,
    GuildConfigResponse,
    AuditLogResponse,
)
from .auth import get_current_user, require_permissions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["api"])


# Card endpoints
@router.get("/cards", response_model=PaginatedResponse[CardResponse])
async def get_cards(
    status: Optional[CardStatus] = None,
    rarity: Optional[CardRarity] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db = Depends(get_db_session),
):
    """Get cards with filtering and pagination."""
    cards = await CardCRUD.get_all(
        db=db,
        status=status,
        rarity=rarity,
        search=search,
        tag=tag,
        limit=limit + 1,  # Get one extra to check if there are more
        offset=offset,
    )
    
    has_more = len(cards) > limit
    if has_more:
        cards = cards[:-1]  # Remove the extra item
    
    card_responses = [CardResponse.from_orm(card) for card in cards]
    
    return PaginatedResponse(
        items=card_responses,
        total=len(card_responses),
        has_more=has_more,
        offset=offset,
        limit=limit,
    )


@router.get("/cards/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: str,
    db = Depends(get_db_session),
):
    """Get a specific card by ID."""
    card = await CardCRUD.get(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    
    return CardResponse.from_orm(card)


@router.post("/cards", response_model=CardResponse)
async def create_card(
    card_data: CardCreate,
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(moderator=True)),
):
    """Create a new card (requires moderator permissions)."""
    card = await CardCRUD.create(
        db=db,
        name=card_data.name,
        description=card_data.description,
        rarity=card_data.rarity,
        image_url=card_data.image_url,
        thumb_url=card_data.thumb_url,
        tags=card_data.tags,
        created_by_user_id=current_user["discord_id"],
        status=CardStatus.APPROVED if card_data.auto_approve else CardStatus.SUBMITTED,
        max_supply=card_data.max_supply,
    )
    
    # Log action
    await AuditLogCRUD.create(
        db=db,
        actor_user_id=current_user["discord_id"],
        action="card_created_via_api",
        target_type="card",
        target_id=card.id,
        meta={
            "name": card.name,
            "rarity": card.rarity.value,
            "auto_approve": card_data.auto_approve,
        },
    )
    
    return CardResponse.from_orm(card)


@router.post("/cards/submit", response_model=dict)
async def submit_card(
    name: str = Form(..., min_length=1, max_length=255),
    description: Optional[str] = Form(None, max_length=500),
    rarity: str = Form(...),
    tags: Optional[str] = Form(None),
    submission_message: Optional[str] = Form(None, max_length=500),
    max_supply: Optional[int] = Form(None, ge=1),
    image: Optional[UploadFile] = File(None),
    db = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """Submit a card for review (regular users)."""
    import os
    import uuid
    from db.models import CardRarity, CardStatus
    
    # Validate rarity
    try:
        card_rarity = CardRarity(rarity.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid rarity: {rarity}. Must be one of: {[r.value for r in CardRarity]}"
        )
    
    # Handle image upload if provided
    image_url = None
    if image:
        # Validate file type and size
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        if image.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file too large (max 10MB)"
            )
        
        # For now, we'll create a placeholder URL
        # In production, you'd upload to cloud storage
        file_extension = os.path.splitext(image.filename)[1]
        image_url = f"/uploads/{uuid.uuid4()}{file_extension}"
    
    # Parse tags
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        if len(tag_list) > 10:
            tag_list = tag_list[:10]  # Limit to 10 tags
    
    # Create the card with SUBMITTED status
    card = await CardCRUD.create(
        db=db,
        name=name,
        description=description,
        rarity=card_rarity,
        image_url=image_url,
        thumb_url=image_url,  # Use same image for thumbnail for now
        tags=tag_list,
        created_by_user_id=current_user["discord_id"],
        status=CardStatus.SUBMITTED,
        max_supply=max_supply,
    )
    
    # Log submission
    await AuditLogCRUD.create(
        db=db,
        actor_user_id=current_user["discord_id"],
        action="card_submitted_via_web",
        target_type="card",
        target_id=card.id,
        meta={
            "name": card.name,
            "rarity": card.rarity.value,
            "submission_message": submission_message,
        },
    )
    
    return {
        "status": "success",
        "message": "Card submitted for review",
        "card": {
            "id": card.id,
            "name": name,
            "rarity": rarity,
            "status": "submitted",
        }
    }


@router.patch("/cards/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: str,
    card_update: CardUpdate,
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(moderator=True)),
):
    """Update a card (requires moderator permissions)."""
    card = await CardCRUD.get(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    
    # Update only provided fields
    update_data = card_update.dict(exclude_unset=True)
    if "tags" in update_data:
        card.tag_list = update_data["tags"]
        del update_data["tags"]
    
    updated_card = await CardCRUD.update(db, card_id, **update_data)
    
    # Log action
    await AuditLogCRUD.create(
        db=db,
        actor_user_id=current_user["discord_id"],
        action="card_updated_via_api",
        target_type="card",
        target_id=card.id,
        meta={"updated_fields": list(update_data.keys())},
    )
    
    return CardResponse.from_orm(updated_card)


@router.post("/cards/{card_id}/approve", response_model=CardResponse)
async def approve_card(
    card_id: str,
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(moderator=True)),
):
    """Approve a submitted card."""
    card = await CardCRUD.approve(db, card_id, current_user["discord_id"])
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found or not in submitted status",
        )
    
    # Log action
    await AuditLogCRUD.create(
        db=db,
        actor_user_id=current_user["discord_id"],
        action="card_approved_via_api",
        target_type="card",
        target_id=card.id,
        meta={"name": card.name},
    )
    
    return CardResponse.from_orm(card)


@router.post("/cards/{card_id}/reject", response_model=CardResponse)
async def reject_card(
    card_id: str,
    reason: Optional[str] = None,
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(moderator=True)),
):
    """Reject a submitted card."""
    card = await CardCRUD.reject(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found or not in submitted status",
        )
    
    # Log action
    await AuditLogCRUD.create(
        db=db,
        actor_user_id=current_user["discord_id"],
        action="card_rejected_via_api",
        target_type="card",
        target_id=card.id,
        meta={"name": card.name, "reason": reason},
    )
    
    return CardResponse.from_orm(card)


# Card instance endpoints
@router.get("/instances", response_model=PaginatedResponse[CardInstanceResponse])
async def get_card_instances(
    user_id: Optional[int] = None,
    active_only: bool = True,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """Get card instances with filtering."""
    # If user_id not specified, show current user's cards
    # If user_id is specified and different from current user, require mod permissions
    target_user_id = user_id or current_user["discord_id"]
    
    if target_user_id != current_user["discord_id"]:
        # Check if user has moderator permissions to view others' cards
        if not current_user.get("is_moderator", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied: cannot view other users' cards",
            )
    
    instances = await CardInstanceCRUD.get_user_instances(
        db=db,
        user_id=target_user_id,
        active_only=active_only,
        limit=limit + 1,
        offset=offset,
    )
    
    has_more = len(instances) > limit
    if has_more:
        instances = instances[:-1]
    
    instance_responses = [CardInstanceResponse.from_orm(instance) for instance in instances]
    
    return PaginatedResponse(
        items=instance_responses,
        total=len(instance_responses),
        has_more=has_more,
        offset=offset,
        limit=limit,
    )


@router.get("/instances/{instance_id}", response_model=CardInstanceResponse)
async def get_card_instance(
    instance_id: str,
    db = Depends(get_db_session),
    current_user = Depends(get_current_user),
):
    """Get a specific card instance."""
    instance = await CardInstanceCRUD.get(db, instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card instance not found",
        )
    
    # Check permissions - user can only see their own instances unless they're a moderator
    if (
        instance.owner_user_id != current_user["discord_id"]
        and not current_user.get("is_moderator", False)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: cannot view this card instance",
        )
    
    return CardInstanceResponse.from_orm(instance)


@router.post("/instances", response_model=CardInstanceResponse)
async def assign_card_instance(
    card_id: str,
    owner_user_id: int,
    expires_in_minutes: Optional[int] = None,
    notes: Optional[str] = None,
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(moderator=True)),
):
    """Assign a card instance to a user (requires moderator permissions)."""
    # Check if card exists and is approved
    card = await CardCRUD.get(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    
    if card.status != CardStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card must be approved before assignment",
        )
    
    # Check supply limit
    if card.max_supply is not None and card.current_supply >= card.max_supply:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Card has reached maximum supply",
        )
    
    # Ensure target user exists
    await UserCRUD.get_or_create(db, owner_user_id)
    
    instance = await CardInstanceCRUD.create(
        db=db,
        card_id=card_id,
        owner_user_id=owner_user_id,
        assigned_by_user_id=current_user["discord_id"],
        expires_in_minutes=expires_in_minutes,
        notes=notes,
    )
    
    # Log action
    await AuditLogCRUD.create(
        db=db,
        actor_user_id=current_user["discord_id"],
        action="card_assigned_via_api",
        target_type="card_instance",
        target_id=instance.id,
        meta={
            "card_name": card.name,
            "card_id": card_id,
            "recipient_id": owner_user_id,
            "expires_in_minutes": expires_in_minutes,
        },
    )
    
    return CardInstanceResponse.from_orm(instance)


@router.delete("/instances/{instance_id}")
async def remove_card_instance(
    instance_id: str,
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(moderator=True)),
):
    """Remove a card instance (requires moderator permissions)."""
    instance = await CardInstanceCRUD.remove(db, instance_id, current_user["discord_id"])
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card instance not found or already removed",
        )
    
    # Log action
    await AuditLogCRUD.create(
        db=db,
        actor_user_id=current_user["discord_id"],
        action="card_instance_removed_via_api",
        target_type="card_instance",
        target_id=instance.id,
        meta={
            "card_name": instance.card.name,
            "owner_id": instance.owner_user_id,
        },
    )
    
    return {"status": "success", "message": "Card instance removed"}


# User endpoints
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
):
    """Get current user information."""
    return UserResponse(
        discord_id=current_user["discord_id"],
        username=current_user.get("username", "Unknown"),
        is_moderator=current_user.get("is_moderator", False),
        is_admin=current_user.get("is_admin", False),
        card_count=current_user.get("card_count", 0),
    )


@router.get("/users/{user_id}/stats")
async def get_user_stats(
    user_id: int,
    db = Depends(get_db_session),
):
    """Get user statistics."""
    instances = await CardInstanceCRUD.get_user_instances(
        db=db, user_id=user_id, active_only=True, limit=1000
    )
    
    # Calculate stats
    total_cards = len(instances)
    rarity_counts = {}
    for instance in instances:
        rarity = instance.card.rarity.value
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
    
    return {
        "user_id": user_id,
        "total_cards": total_cards,
        "rarity_breakdown": rarity_counts,
        "last_activity": max(
            (instance.assigned_at for instance in instances), default=None
        ),
    }


# Leaderboard endpoint
@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(10, le=100),
    db = Depends(get_db_session),
):
    """Get card collection leaderboard."""
    leaderboard_data = await CardInstanceCRUD.get_card_leaderboard(
        db=db, limit=limit, active_only=True
    )
    
    return {
        "leaderboard": [
            {"user_id": user_id, "card_count": count}
            for user_id, count in leaderboard_data
        ]
    }


# Search endpoint
@router.get("/search")
async def search_cards(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, le=50),
    db = Depends(get_db_session),
):
    """Search cards by name, description, or tags."""
    cards = await CardCRUD.search(db=db, query=q, limit=limit)
    card_responses = [CardResponse.from_orm(card) for card in cards]
    
    return {
        "query": q,
        "results": card_responses,
        "count": len(card_responses),
    }


# Admin endpoints
@router.get("/admin/audit-logs", response_model=PaginatedResponse[AuditLogResponse])
async def get_audit_logs(
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(50, le=200),
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(admin=True)),
):
    """Get audit logs (requires admin permissions)."""
    if user_id:
        logs = await AuditLogCRUD.get_user_actions(
            db=db, user_id=user_id, limit=limit, actions=[action] if action else None
        )
    else:
        logs = await AuditLogCRUD.get_recent_actions(
            db=db, limit=limit, action=action, days=days
        )
    
    log_responses = [AuditLogResponse.from_orm(log) for log in logs]
    
    return PaginatedResponse(
        items=log_responses,
        total=len(log_responses),
        has_more=len(log_responses) == limit,
        offset=0,
        limit=limit,
    )


@router.get("/admin/stats")
async def get_admin_stats(
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(admin=True)),
):
    """Get administrative statistics."""
    # This would calculate various system statistics
    # For now, just return basic counts
    
    total_cards_result = await db.execute("SELECT COUNT(*) FROM cards")
    total_cards = total_cards_result.scalar()
    
    total_instances_result = await db.execute(
        "SELECT COUNT(*) FROM card_instances WHERE removed_at IS NULL"
    )
    total_instances = total_instances_result.scalar()
    
    total_users_result = await db.execute("SELECT COUNT(*) FROM users")
    total_users = total_users_result.scalar()
    
    return {
        "total_cards": total_cards,
        "total_instances": total_instances,
        "total_users": total_users,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Guild configuration endpoints
@router.get("/admin/guild/{guild_id}/config", response_model=GuildConfigResponse)
async def get_guild_config(
    guild_id: int,
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(admin=True)),
):
    """Get guild configuration."""
    config = await GuildConfigCRUD.get_or_create(db, guild_id)
    return GuildConfigResponse.from_orm(config)


@router.patch("/admin/guild/{guild_id}/config", response_model=GuildConfigResponse)
async def update_guild_config(
    guild_id: int,
    config_update: dict,
    db = Depends(get_db_session),
    current_user = Depends(require_permissions(admin=True)),
):
    """Update guild configuration."""
    config = await GuildConfigCRUD.update_config(db, guild_id, **config_update)
    
    # Log action
    await AuditLogCRUD.create(
        db=db,
        actor_user_id=current_user["discord_id"],
        action="guild_config_updated",
        target_type="guild_config",
        target_id=str(guild_id),
        meta={"updated_fields": list(config_update.keys())},
    )
    
    return GuildConfigResponse.from_orm(config)