from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    full_name: str
    company_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    full_name: Optional[str] = None
    company_name: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    email_verified: bool
    created_at: datetime
    updated_at: datetime


# Auth schemas
class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class PasswordResetRequest(BaseSchema):
    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    token: str
    new_password: str = Field(..., min_length=8)


# Candidate schemas
class CandidateBase(BaseSchema):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    skills: Optional[List[str]] = []
    experience_years: Optional[int] = 0
    education_level: Optional[str] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: Optional[str] = "new"
    source: Optional[str] = None
    notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    resume_text: Optional[str] = None


class CandidateUpdate(BaseSchema):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class CandidateStatusUpdate(BaseSchema):
    status: str


class CandidateResponse(CandidateBase):
    id: UUID
    user_id: UUID
    resume_url: Optional[str] = None
    resume_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CandidateListResponse(BaseSchema):
    items: List[CandidateResponse]
    total: int
    page: int
    page_size: int


class ResumeUploadResponse(BaseSchema):
    resume_url: str
    resume_text: str
    extracted_data: Dict[str, Any]


# Job Position schemas
class JobPositionBase(BaseSchema):
    title: str
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = {}
    department: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: Optional[str] = "open"


class JobPositionCreate(JobPositionBase):
    pass


class JobPositionUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    department: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    status: Optional[str] = None


class JobPositionResponse(JobPositionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class JobPositionListResponse(BaseSchema):
    items: List[JobPositionResponse]
    total: int


# Scoring schemas
class ScoreRequest(BaseSchema):
    candidate_id: UUID
    job_position_id: Optional[UUID] = None


class BulkScoreRequest(BaseSchema):
    candidate_ids: List[UUID]
    job_position_id: Optional[UUID] = None


class ScoreBreakdown(BaseSchema):
    skills_match: Dict[str, Any]
    experience_match: Dict[str, Any]
    education_match: Dict[str, Any]


class ScoreResponse(BaseSchema):
    id: UUID
    candidate_id: UUID
    job_position_id: Optional[UUID] = None
    skills_score: int
    experience_score: int
    education_score: int
    overall_score: int
    breakdown: Dict[str, Any]
    created_at: datetime


# Email Template schemas
class EmailTemplateBase(BaseSchema):
    name: str
    subject: str
    body: str
    variables: Optional[List[str]] = []


class EmailTemplateCreate(EmailTemplateBase):
    pass


class EmailTemplateUpdate(BaseSchema):
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    variables: Optional[List[str]] = None


class EmailTemplateResponse(EmailTemplateBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


# Outreach schemas
class SendEmailRequest(BaseSchema):
    candidate_id: UUID
    template_id: Optional[UUID] = None
    job_position_id: Optional[UUID] = None
    subject: Optional[str] = None
    body: Optional[str] = None


class BulkEmailRequest(BaseSchema):
    candidate_ids: List[UUID]
    template_id: Optional[UUID] = None
    job_position_id: Optional[UUID] = None


class SentEmailResponse(BaseSchema):
    id: UUID
    user_id: UUID
    candidate_id: UUID
    template_id: Optional[UUID] = None
    job_position_id: Optional[UUID] = None
    subject: str
    body: str
    status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    created_at: datetime


class EmailStatsResponse(BaseSchema):
    total_sent: int
    total_delivered: int
    total_opened: int
    total_replied: int
    total_failed: int
    delivery_rate: float
    open_rate: float
    reply_rate: float


# Dashboard schemas
class DashboardOverview(BaseSchema):
    total_candidates: int
    active_candidates: int
    total_jobs: int
    open_jobs: int
    total_emails_sent: int
    email_open_rate: float


class PipelineStage(BaseSchema):
    status: str
    count: int
    label: str


class DashboardPipeline(BaseSchema):
    stages: List[PipelineStage]
    total: int


class HiringMetrics(BaseSchema):
    avg_time_to_hire: Optional[float]
    total_hired: int
    total_rejected: int
    offer_acceptance_rate: float
    candidates_per_position: float


class ActivityItem(BaseSchema):
    id: UUID
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    details: Dict[str, Any]
    created_at: datetime


class DashboardActivity(BaseSchema):
    items: List[ActivityItem]
    total: int


# Common response
class MessageResponse(BaseSchema):
    message: str
    success: bool = True
