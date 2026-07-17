"""
Team management API routes.
"""
import secrets
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.config import settings
from app.models import User, Subscription, TeamMember, ActivityLog
from app.schemas.saas_schemas import (
    TeamMemberInvite,
    TeamMemberUpdate,
    TeamMemberResponse,
    TeamMemberListResponse,
    InviteResponse,
)
from app.services.stripe_service import PLAN_LIMITS

router = APIRouter(prefix="/api/teams", tags=["teams"])


async def get_user_subscription(db: AsyncSession, user: User) -> tuple[Subscription, dict]:
    """Get user's subscription with plan limits."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # Create trial subscription for new users
        from datetime import timedelta
        subscription = Subscription(
            id=uuid4(),
            user_id=user.id,
            plan_type="trial",
            status="trialing",
            trial_end=datetime.utcnow() + timedelta(days=settings.TRIAL_DAYS),
        )
        db.add(subscription)
        await db.flush()
    
    # Get plan limits
    plan = subscription.plan_type if subscription.plan_type != "trial" else "professional"
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["professional"])
    
    return subscription, limits


@router.get("", response_model=TeamMemberListResponse)
async def list_team_members(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all team members."""
    subscription, limits = await get_user_subscription(db, current_user)
    
    result = await db.execute(
        select(TeamMember)
        .where(TeamMember.subscription_id == subscription.id)
        .where(TeamMember.status != "removed")
        .order_by(TeamMember.created_at.desc())
    )
    members = result.scalars().all()
    
    # Count active members
    active_count = sum(1 for m in members if m.status == "active")
    
    return TeamMemberListResponse(
        members=[TeamMemberResponse.model_validate(m) for m in members],
        total=len(members),
        seats_used=active_count,
        seats_total=limits["team_seats"],
    )


@router.post("/invite", response_model=InviteResponse)
async def invite_team_member(
    invite: TeamMemberInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Invite a new team member."""
    subscription, limits = await get_user_subscription(db, current_user)
    
    # Check seat limit
    result = await db.execute(
        select(func.count(TeamMember.id))
        .where(TeamMember.subscription_id == subscription.id)
        .where(TeamMember.status == "active")
    )
    active_count = result.scalar()
    
    if active_count >= limits["team_seats"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Team seat limit reached ({limits['team_seats']}). Upgrade to add more members."
        )
    
    # Check if already invited
    result = await db.execute(
        select(TeamMember)
        .where(TeamMember.subscription_id == subscription.id)
        .where(TeamMember.email == invite.email)
        .where(TeamMember.status != "removed")
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        if existing.status == "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already a team member."
            )
        # Re-use existing pending invitation
        existing.invite_token = secrets.token_urlsafe(32)
        existing.invited_at = datetime.utcnow()
        existing.role = invite.role
        existing.name = invite.name
    else:
        # Create new invitation
        invite_token = secrets.token_urlsafe(32)
        member = TeamMember(
            id=uuid4(),
            subscription_id=subscription.id,
            email=invite.email,
            name=invite.name,
            role=invite.role,
            status="pending",
            invite_token=invite_token,
            invited_at=datetime.utcnow(),
        )
        db.add(member)
    
    await db.flush()
    
    # Log activity
    log = ActivityLog(
        id=uuid4(),
        user_id=current_user.id,
        action="team_invite_sent",
        entity_type="team_member",
        details={"email": invite.email, "role": invite.role},
    )
    db.add(log)
    
    await db.commit()
    
    invite_url = f"{settings.FRONTEND_URL}/join?token={invite_token}"
    
    return InviteResponse(
        message=f"Invitation sent to {invite.email}",
        invite_url=invite_url,
    )


@router.put("/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    member_id: str,
    update: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a team member's role."""
    subscription, _ = await get_user_subscription(db, current_user)
    
    result = await db.execute(
        select(TeamMember)
        .where(TeamMember.id == member_id)
        .where(TeamMember.subscription_id == subscription.id)
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found."
        )
    
    if update.role:
        member.role = update.role
    
    await db.commit()
    
    return TeamMemberResponse.model_validate(member)


@router.delete("/{member_id}")
async def remove_team_member(
    member_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a team member."""
    subscription, _ = await get_user_subscription(db, current_user)
    
    result = await db.execute(
        select(TeamMember)
        .where(TeamMember.id == member_id)
        .where(TeamMember.subscription_id == subscription.id)
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found."
        )
    
    if member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove the owner."
        )
    
    member.status = "removed"
    member.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Team member removed."}


@router.post("/accept")
async def accept_invitation(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a team invitation."""
    result = await db.execute(
        select(TeamMember).where(TeamMember.invite_token == token)
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invitation."
        )
    
    if member.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation already accepted."
        )
    
    if member.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation is for a different email address."
        )
    
    member.status = "active"
    member.joined_at = datetime.utcnow()
    member.invite_token = None
    
    # Log activity
    log = ActivityLog(
        id=uuid4(),
        user_id=current_user.id,
        action="team_joined",
        entity_type="team_member",
        details={"email": member.email},
    )
    db.add(log)
    
    await db.commit()
    
    return {"message": "Welcome to the team!"}
