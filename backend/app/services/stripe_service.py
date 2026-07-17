"""
Stripe subscription service for Recruiter In A Box.
Handles subscription management, checkout, and webhooks.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings


# Stripe Price IDs (configure in environment)
STRIPE_PRICES = {
    "professional": os.getenv("STRIPE_PRICE_PROFESSIONAL", "price_professional"),
    "agency": os.getenv("STRIPE_PRICE_AGENCY", "price_agency"),
}

# Plan limits
PLAN_LIMITS = {
    "professional": {
        "candidates_per_month": 100,
        "job_positions": 10,
        "team_seats": 1,
        "ai_scoring": True,
        "email_outreach": True,
        "analytics": "basic",
        "support": "email",
    },
    "agency": {
        "candidates_per_month": -1,  # Unlimited
        "job_positions": -1,  # Unlimited
        "team_seats": 5,
        "ai_scoring": True,
        "email_outreach": True,
        "analytics": "advanced",
        "support": "priority",
        "custom_branding": True,
    },
}


class StripeService:
    def __init__(self):
        self.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self.price_ids = STRIPE_PRICES
        self.base_url = "https://api.stripe.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    async def create_customer(self, email: str, name: str, metadata: dict = None) -> dict:
        """Create a new Stripe customer."""
        async with httpx.AsyncClient() as client:
            data = {
                "email": email,
                "name": name,
            }
            if metadata:
                for key, value in metadata.items():
                    data[f"metadata[{key}]"] = str(value)
            
            response = await client.post(
                f"{self.base_url}/customers",
                headers=self.headers,
                data=data,
            )
            return response.json()

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: int = 14,
    ) -> dict:
        """Create a Stripe Checkout session for subscription."""
        async with httpx.AsyncClient() as client:
            data = {
                "customer": customer_id,
                "mode": "subscription",
                "line_items[0][price]": price_id,
                "line_items[0][quantity]": "1",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "allow_promotion_codes": "true",
                "billing_address_collection": "required",
            }
            
            if trial_days > 0:
                data["subscription_data[trial_period_days]"] = str(trial_days)
            
            response = await client.post(
                f"{self.base_url}/checkout/sessions",
                headers=self.headers,
                data=data,
            )
            return response.json()

    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> dict:
        """Create a Stripe Billing Portal session."""
        async with httpx.AsyncClient() as client:
            data = {
                "customer": customer_id,
                "return_url": return_url,
            }
            response = await client.post(
                f"{self.base_url}/billing_portal/sessions",
                headers=self.headers,
                data=data,
            )
            return response.json()

    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = True,
    ) -> dict:
        """Cancel a subscription."""
        async with httpx.AsyncClient() as client:
            if cancel_at_period_end:
                data = {"cancel_at_period_end": "true"}
            else:
                data = {"cancel_immediately": "true"}
            
            response = await client.post(
                f"{self.base_url}/subscriptions/{subscription_id}",
                headers=self.headers,
                data=data,
            )
            return response.json()

    async def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str,
    ) -> dict:
        """Update subscription to a new price."""
        async with httpx.AsyncClient() as client:
            data = {
                "items[0][id]": "TODO",  # Will be populated from subscription
                "items[0][price]": new_price_id,
                "proration_behavior": "create_prorations",
            }
            response = await client.post(
                f"{self.base_url}/subscriptions/{subscription_id}",
                headers=self.headers,
                data=data,
            )
            return response.json()

    async def get_subscription(self, subscription_id: str) -> dict:
        """Get subscription details."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/subscriptions/{subscription_id}",
                headers=self.headers,
            )
            return response.json()

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> dict:
        """Verify webhook signature and return event."""
        import stripe
        
        if not self.api_key:
            return None
            
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except Exception:
            return None

    def get_plan_limits(self, plan: str) -> dict:
        """Get limits for a specific plan."""
        return PLAN_LIMITS.get(plan, PLAN_LIMITS["professional"])

    async def check_usage_within_limits(
        self,
        db: AsyncSession,
        user_id: str,
        resource: str,
    ) -> tuple[bool, str]:
        """
        Check if user is within their plan limits.
        Returns (is_within_limits, message)
        """
        from app.models import User, Subscription, Candidate
        
        # Get user with subscription
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.subscription:
            return False, "No active subscription"
        
        plan = user.subscription.plan_type
        limits = self.get_plan_limits(plan)
        
        if resource == "candidate":
            # Count candidates this month
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            result = await db.execute(
                select(Candidate).where(
                    Candidate.user_id == user_id,
                    Candidate.created_at >= month_start,
                )
            )
            candidates_count = len(result.scalars().all())
            limit = limits["candidates_per_month"]
            
            if limit > 0 and candidates_count >= limit:
                return False, f"Monthly candidate limit reached ({limit}). Upgrade to add more."
        
        return True, "OK"


stripe_service = StripeService()
