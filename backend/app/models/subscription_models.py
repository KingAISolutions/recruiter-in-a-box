"""
Additional models for SaaS features: subscriptions, teams, interviews, onboarding.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Subscription(Base):
    """User subscription model for billing."""
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    plan_type = Column(String(50), nullable=False, default="trial")  # trial, professional, agency
    status = Column(String(50), nullable=False, default="active")  # active, canceled, past_due, trialing
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")
    team_members = relationship("TeamMember", back_populates="subscription", cascade="all, delete-orphan")


class TeamMember(Base):
    """Team members for collaborative recruitment."""
    __tablename__ = "team_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="member")  # owner, admin, member
    status = Column(String(50), nullable=False, default="pending")  # pending, active, removed
    invite_token = Column(String(255), nullable=True)
    invited_at = Column(DateTime, nullable=True)
    joined_at = Column(DateTime, nullable=True)
    last_active_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="team_members")


class Interview(Base):
    """Interview scheduling for candidates."""
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_position_id = Column(UUID(as_uuid=True), ForeignKey("job_positions.id", ondelete="SET NULL"), nullable=True)
    
    # Interview details
    title = Column(String(255), nullable=True)
    interview_type = Column(String(50), nullable=True)  # phone, video, onsite, technical
    scheduled_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=60)
    location = Column(String(255), nullable=True)  # URL for video or physical location
    
    # Status
    status = Column(String(50), nullable=False, default="scheduled")  # scheduled, confirmed, completed, canceled, rescheduled
    
    # Notes and feedback
    notes = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5
    
    # Calendar integration
    calendar_event_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate")
    user = relationship("User")
    job_position = relationship("JobPosition")


class OnboardingProgress(Base):
    """Track user onboarding progress."""
    __tablename__ = "onboarding_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Step completion flags
    step_profile_completed = Column(Boolean, default=False)
    step_first_job_completed = Column(Boolean, default=False)
    step_first_candidate_completed = Column(Boolean, default=False)
    step_first_email_completed = Column(Boolean, default=False)
    step_integration_completed = Column(Boolean, default=False)
    
    # Current step
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, default=5)
    
    # Tour tracking
    tour_completed = Column(Boolean, default=False)
    tour_dismissed_at = Column(DateTime, nullable=True)
    
    # Welcome email tracking
    welcome_email_sent = Column(Boolean, default=False)
    welcome_email_sent_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")


class EmailTracking(Base):
    """Track email opens and clicks for analytics."""
    __tablename__ = "email_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sent_email_id = Column(UUID(as_uuid=True), ForeignKey("sent_emails.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Tracking events
    tracking_id = Column(String(255), nullable=False, unique=True)  # Unique ID for tracking pixel/link
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Events
    opened = Column(Boolean, default=False)
    opened_at = Column(DateTime, nullable=True)
    click_count = Column(Integer, default=0)
    
    # Link tracking
    links_clicked = Column(JSON, default=list)  # List of URLs clicked
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sent_email = relationship("SentEmail")
    user = relationship("User")


class ResumeSummary(Base):
    """AI-generated resume summaries."""
    __tablename__ = "resume_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # AI-generated content
    summary = Column(Text, nullable=True)
    key_strengths = Column(JSON, default=list)
    potential_concerns = Column(JSON, default=list)
    recommended_next_steps = Column(JSON, default=list)
    
    # Metadata
    model_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_usd = Column(Integer, nullable=True)  # Cost in cents
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate")
    user = relationship("User")
