"""
Subscription management API routes.
"""
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models import User, Subscription
from app.services.stripe_service import stripe_service, PLAN_LIMITS
from app.schemas.saas_schemas import (
    SubscriptionResponse,
    SubscriptionCheckoutResponse,
    SubscriptionPortalResponse,
    SubscriptionStatusResponse,
    PlanLimits,
)

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


def get_or_create_subscription(db: AsyncSession, user: User) -> Subscription:
    """Get existing subscription or create a new trial subscription."""
    # Check for existing subscription
    result = db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # Create new trial subscription
        subscription = Subscription(
            id=uuid4(),
            user_id=user.id,
            plan_type="trial",
            status="trialing",
            trial_end=datetime.utcnow() + timedelta(days=settings.TRIAL_DAYS),
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=settings.TRIAL_DAYS),
        )
        db.add(subscription)
        # Create user subscription relationship
        user.subscription = subscription
    
    return subscription


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current subscription status and limits."""
    subscription = get_or_create_subscription(db, current_user)
    
    # Determine effective plan
    if subscription.plan_type == "trial":
        plan = "professional"  # Trial gives access to professional features
        trial_days_remaining = max(0, (subscription.trial_end - datetime.utcnow()).days)
        trial_expired = trial_days_remaining <= 0
    else:
        plan = subscription.plan_type
        trial_days_remaining = None
        trial_expired = False
    
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["professional"])
    
    return SubscriptionStatusResponse(
        subscription=subscription,
        plan_limits=PlanLimits(**limits),
        trial_days_remaining=trial_days_remaining,
        trial_expired=trial_expired,
    )


@router.post("/checkout", response_model=SubscriptionCheckoutResponse)
async def create_checkout_session(
    plan: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe checkout session for subscription."""
    # Validate plan
    if plan not in ["professional", "agency"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan. Choose 'professional' or 'agency'."
        )
    
    # Check if Stripe is configured
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing is not available. Please try again later."
        )
    
    # Get or create subscription
    subscription = get_or_create_subscription(db, current_user)
    
    # Create Stripe customer if not exists
    if not subscription.stripe_customer_id:
        try:
            customer = await stripe_service.create_customer(
                email=current_user.email,
                name=current_user.full_name,
                metadata={"user_id": str(current_user.id)}
            )
            subscription.stripe_customer_id = customer["id"]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create customer: {str(e)}"
            )
    
    # Get price ID
    price_id = settings.STRIPE_PRICE_PROFESSIONAL if plan == "professional" else settings.STRIPE_PRICE_AGENCY
    
    # Create checkout session
    try:
        session = await stripe_service.create_checkout_session(
            customer_id=subscription.stripe_customer_id,
            price_id=price_id,
            success_url=f"{settings.FRONTEND_URL}/dashboard?subscription=success",
            cancel_url=f"{settings.FRONTEND_URL}/settings?subscription=canceled",
            trial_days=0,  # No trial on upgrade
        )
        
        db.commit()
        
        return SubscriptionCheckoutResponse(
            checkout_url=session["url"],
            session_id=session["id"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/portal", response_model=SubscriptionPortalResponse)
async def create_billing_portal(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe billing portal session."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing is not available."
        )
    
    subscription = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = subscription.scalar_one_or_none()
    
    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found."
        )
    
    try:
        session = await stripe_service.create_billing_portal_session(
            customer_id=subscription.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/settings",
        )
        
        return SubscriptionPortalResponse(portal_url=session["url"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create portal session: {str(e)}"
        )


@router.post("/cancel")
async def cancel_subscription(
    cancel_now: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel the current subscription."""
    subscription = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = subscription.scalar_one_or_none()
    
    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found."
        )
    
    if not settings.STRIPE_SECRET_KEY:
        # Simulate cancellation for development
        subscription.status = "canceled"
        subscription.cancel_at_period_end = not cancel_now
        db.commit()
        return {"message": "Subscription canceled."}
    
    try:
        await stripe_service.cancel_subscription(
            subscription_id=subscription.stripe_subscription_id,
            cancel_at_period_end=not cancel_now,
        )
        
        subscription.cancel_at_period_end = not cancel_now
        db.commit()
        
        return {"message": "Subscription canceled."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )
