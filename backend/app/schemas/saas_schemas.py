"""
Pydantic schemas for SaaS features: subscriptions, teams, interviews, onboarding.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ============== Subscription Schemas ==============

class SubscriptionBase(BaseSchema):
    plan_type: str = "trial"
    status: str = "active"


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionUpdate(BaseSchema):
    plan_type: Optional[str] = None
    status: Optional[str] = None


class SubscriptionResponse(SubscriptionBase):
    id: UUID
    user_id: UUID
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    created_at: datetime
    updated_at: datetime


class SubscriptionCheckoutResponse(BaseSchema):
    checkout_url: str
    session_id: str


class SubscriptionPortalResponse(BaseSchema):
    portal_url: str


class PlanLimits(BaseSchema):
    candidates_per_month: int
    job_positions: int
    team_seats: int
    ai_scoring: bool
    email_outreach: bool
    analytics: str
    support: str
    custom_branding: Optional[bool] = False


class SubscriptionStatusResponse(BaseSchema):
    subscription: Optional[SubscriptionResponse] = None
    plan_limits: PlanLimits
    trial_days_remaining: Optional[int] = None
    trial_expired: bool = False


# ============== Team Member Schemas ==============

class TeamMemberBase(BaseSchema):
    email: EmailStr
    name: Optional[str] = None
    role: str = "member"


class TeamMemberInvite(BaseSchema):
    email: EmailStr
    name: Optional[str] = None
    role: str = "member"


class TeamMemberUpdate(BaseSchema):
    role: Optional[str] = None


class TeamMemberResponse(TeamMemberBase):
    id: UUID
    subscription_id: UUID
    status: str
    invite_token: Optional[str] = None
    invited_at: Optional[datetime] = None
    joined_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    created_at: datetime


class TeamMemberListResponse(BaseSchema):
    members: List[TeamMemberResponse]
    total: int
    seats_used: int
    seats_total: int


class InviteResponse(BaseSchema):
    message: str
    invite_url: str


# ============== Interview Schemas ==============

class InterviewBase(BaseSchema):
    candidate_id: UUID
    title: Optional[str] = None
    interview_type: Optional[str] = "video"
    scheduled_at: datetime
    duration_minutes: int = 60
    location: Optional[str] = None


class InterviewCreate(InterviewBase):
    job_position_id: Optional[UUID] = None
    notes: Optional[str] = None


class InterviewUpdate(BaseSchema):
    title: Optional[str] = None
    interview_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class InterviewResponse(BaseSchema):
    id: UUID
    candidate_id: UUID
    user_id: UUID
    job_position_id: Optional[UUID] = None
    title: Optional[str] = None
    interview_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: int = 60
    location: Optional[str] = None
    status: str
    notes: Optional[str] = None
    feedback: Optional[str] = None
    rating: Optional[int] = None
    calendar_event_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class InterviewListResponse(BaseSchema):
    interviews: List[InterviewResponse]
    total: int
    upcoming: int
    completed: int


# ============== Onboarding Schemas ==============

class OnboardingProgressResponse(BaseSchema):
    step_profile_completed: bool = False
    step_first_job_completed: bool = False
    step_first_candidate_completed: bool = False
    step_first_email_completed: bool = False
    step_integration_completed: bool = False
    current_step: int = 1
    total_steps: int = 5
    tour_completed: bool = False
    tour_dismissed_at: Optional[datetime] = None
    progress_percentage: int = 0


class OnboardingStepComplete(BaseSchema):
    step: str  # profile, first_job, first_candidate, first_email, integration


class OnboardingDismissTour(BaseSchema):
    pass


# ============== Email Tracking Schemas ==============

class EmailTrackingEvent(BaseSchema):
    tracking_id: str
    event_type: str  # open, click
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    link_url: Optional[str] = None


class EmailTrackingResponse(BaseSchema):
    id: UUID
    sent_email_id: UUID
    tracking_id: str
    opened: bool = False
    opened_at: Optional[datetime] = None
    click_count: int = 0
    links_clicked: List[str] = []


# ============== Resume Summary Schemas ==============

class ResumeSummaryResponse(BaseSchema):
    id: UUID
    candidate_id: UUID
    summary: Optional[str] = None
    key_strengths: List[str] = []
    potential_concerns: List[str] = []
    recommended_next_steps: List[str] = []
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    created_at: datetime


class ResumeSummaryGenerate(BaseSchema):
    candidate_id: UUID


# ============== Admin Schemas ==============

class AdminDashboardStats(BaseSchema):
    total_users: int
    active_subscriptions: int
    trial_users: int
    paid_users: int
    total_candidates: int
    total_emails_sent: int
    monthly_revenue: float
    churn_rate: float


class AdminUserResponse(BaseSchema):
    id: UUID
    email: str
    full_name: str
    company_name: Optional[str] = None
    subscription_status: Optional[str] = None
    plan_type: Optional[str] = None
    created_at: datetime
    last_active: Optional[datetime] = None


class AdminUserListResponse(BaseSchema):
    users: List[AdminUserResponse]
    total: int
    page: int
    page_size: int


class AdminSubscriptionUpdate(BaseSchema):
    plan_type: str
    status: str
    trial_end: Optional[datetime] = None


# ============== Webhook Schemas ==============

class StripeWebhookEvent(BaseSchema):
    type: str
    data: Dict[str, Any]
