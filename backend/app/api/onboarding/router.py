"""
Onboarding API routes.
"""
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, OnboardingProgress, Candidate, JobPosition, EmailTemplate, ActivityLog
from app.schemas.saas_schemas import (
    OnboardingProgressResponse,
    OnboardingStepComplete,
)

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

# Step mappings
STEP_MAP = {
    "profile": "step_profile_completed",
    "first_job": "step_first_job_completed",
    "first_candidate": "step_first_candidate_completed",
    "first_email": "step_first_email_completed",
    "integration": "step_integration_completed",
}


async def get_or_create_progress(db: AsyncSession, user: User) -> OnboardingProgress:
    """Get or create onboarding progress."""
    result = await db.execute(
        select(OnboardingProgress).where(OnboardingProgress.user_id == user.id)
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        progress = OnboardingProgress(
            id=uuid4(),
            user_id=user.id,
            current_step=1,
            total_steps=5,
        )
        db.add(progress)
        await db.flush()
    
    return progress


def calculate_progress(progress: OnboardingProgress) -> int:
    """Calculate progress percentage."""
    completed = sum([
        progress.step_profile_completed,
        progress.step_first_job_completed,
        progress.step_first_candidate_completed,
        progress.step_first_email_completed,
        progress.step_integration_completed,
    ])
    return int((completed / progress.total_steps) * 100)


@router.get("", response_model=OnboardingProgressResponse)
async def get_onboarding_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current onboarding progress."""
    progress = await get_or_create_progress(db, current_user)
    
    return OnboardingProgressResponse(
        step_profile_completed=progress.step_profile_completed,
        step_first_job_completed=progress.step_first_job_completed,
        step_first_candidate_completed=progress.step_first_candidate_completed,
        step_first_email_completed=progress.step_first_email_completed,
        step_integration_completed=progress.step_integration_completed,
        current_step=progress.current_step,
        total_steps=progress.total_steps,
        tour_completed=progress.tour_completed,
        tour_dismissed_at=progress.tour_dismissed_at,
        progress_percentage=calculate_progress(progress),
    )


@router.post("/complete-step")
async def complete_onboarding_step(
    step_complete: OnboardingStepComplete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an onboarding step as completed."""
    step_field = STEP_MAP.get(step_complete.step)
    
    if not step_field:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid step. Must be one of: {', '.join(STEP_MAP.keys())}"
        )
    
    progress = await get_or_create_progress(db, current_user)
    
    # Mark step as completed
    setattr(progress, step_field, True)
    
    # Update current step
    steps = list(STEP_MAP.values())
    current_index = steps.index(step_field) if step_field in steps else 0
    progress.current_step = min(current_index + 2, progress.total_steps)
    
    progress.updated_at = datetime.utcnow()
    
    # Log activity
    log = ActivityLog(
        id=uuid4(),
        user_id=current_user.id,
        action="onboarding_step_completed",
        details={"step": step_complete.step},
    )
    db.add(log)
    
    await db.commit()
    
    return {
        "message": f"Step '{step_complete.step}' completed",
        "progress_percentage": calculate_progress(progress),
    }


@router.post("/check-step")
async def check_onboarding_steps(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Automatically check and update onboarding progress based on user actions.
    This should be called when relevant actions are performed.
    """
    progress = await get_or_create_progress(db, current_user)
    
    # Check profile completion
    if not progress.step_profile_completed and current_user.full_name and current_user.company_name:
        progress.step_profile_completed = True
    
    # Check first job
    if not progress.step_first_job_completed:
        result = await db.execute(
            select(JobPosition).where(JobPosition.user_id == current_user.id).limit(1)
        )
        if result.scalar_one_or_none():
            progress.step_first_job_completed = True
    
    # Check first candidate
    if not progress.step_first_candidate_completed:
        result = await db.execute(
            select(Candidate).where(Candidate.user_id == current_user.id).limit(1)
        )
        if result.scalar_one_or_none():
            progress.step_first_candidate_completed = True
    
    # Check first email
    if not progress.step_first_email_completed:
        result = await db.execute(
            select(EmailTemplate).where(EmailTemplate.user_id == current_user.id).limit(1)
        )
        if result.scalar_one_or_none():
            progress.step_first_email_completed = True
    
    # Update current step
    steps_completed = sum([
        progress.step_profile_completed,
        progress.step_first_job_completed,
        progress.step_first_candidate_completed,
        progress.step_first_email_completed,
        progress.step_integration_completed,
    ])
    progress.current_step = min(steps_completed + 1, progress.total_steps)
    
    progress.updated_at = datetime.utcnow()
    await db.commit()
    
    return {
        "progress_percentage": calculate_progress(progress),
        "steps": {
            "profile": progress.step_profile_completed,
            "first_job": progress.step_first_job_completed,
            "first_candidate": progress.step_first_candidate_completed,
            "first_email": progress.step_first_email_completed,
            "integration": progress.step_integration_completed,
        },
    }


@router.post("/dismiss-tour")
async def dismiss_onboarding_tour(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dismiss the onboarding tour."""
    progress = await get_or_create_progress(db, current_user)
    
    progress.tour_completed = True
    progress.tour_dismissed_at = datetime.utcnow()
    progress.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Tour dismissed"}


@router.post("/reset")
async def reset_onboarding(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reset onboarding progress (for testing)."""
    progress = await get_or_create_progress(db, current_user)
    
    progress.step_profile_completed = False
    progress.step_first_job_completed = False
    progress.step_first_candidate_completed = False
    progress.step_first_email_completed = False
    progress.step_integration_completed = False
    progress.current_step = 1
    progress.tour_completed = False
    progress.tour_dismissed_at = None
    progress.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Onboarding progress reset"}
