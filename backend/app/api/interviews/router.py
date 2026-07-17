"""
Interview scheduling API routes.
"""
from datetime import datetime
from uuid import uuid4
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Interview, Candidate, JobPosition, ActivityLog
from app.schemas.saas_schemas import (
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse,
    InterviewListResponse,
)

router = APIRouter(prefix="/api/interviews", tags=["interviews"])


@router.get("", response_model=InterviewListResponse)
async def list_interviews(
    status_filter: Optional[str] = Query(None, alias="status"),
    candidate_id: Optional[str] = Query(None),
    upcoming_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all interviews."""
    query = select(Interview).where(Interview.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Interview.status == status_filter)
    
    if candidate_id:
        query = query.where(Interview.candidate_id == candidate_id)
    
    if upcoming_only:
        query = query.where(
            and_(
                Interview.scheduled_at >= datetime.utcnow(),
                Interview.status.in_(["scheduled", "confirmed"])
            )
        )
    
    query = query.order_by(Interview.scheduled_at.asc())
    
    result = await db.execute(query)
    interviews = result.scalars().all()
    
    upcoming = sum(
        1 for i in interviews 
        if i.scheduled_at and i.scheduled_at >= datetime.utcnow() 
        and i.status in ["scheduled", "confirmed"]
    )
    completed = sum(1 for i in interviews if i.status == "completed")
    
    return InterviewListResponse(
        interviews=[InterviewResponse.model_validate(i) for i in interviews],
        total=len(interviews),
        upcoming=upcoming,
        completed=completed,
    )


@router.post("", response_model=InterviewResponse)
async def create_interview(
    interview: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Schedule a new interview."""
    # Verify candidate exists
    result = await db.execute(
        select(Candidate).where(Candidate.id == interview.candidate_id)
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found."
        )
    
    # Verify job position if provided
    if interview.job_position_id:
        result = await db.execute(
            select(JobPosition).where(JobPosition.id == interview.job_position_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job position not found."
            )
    
    db_interview = Interview(
        id=uuid4(),
        candidate_id=interview.candidate_id,
        user_id=current_user.id,
        job_position_id=interview.job_position_id,
        title=interview.title or f"Interview with {candidate.full_name}",
        interview_type=interview.interview_type,
        scheduled_at=interview.scheduled_at,
        duration_minutes=interview.duration_minutes,
        location=interview.location,
        status="scheduled",
        notes=interview.notes,
    )
    db.add(db_interview)
    
    # Update candidate status
    candidate.status = "interview"
    
    # Log activity
    log = ActivityLog(
        id=uuid4(),
        user_id=current_user.id,
        action="interview_scheduled",
        entity_type="candidate",
        entity_id=candidate.id,
        details={
            "candidate_name": candidate.full_name,
            "scheduled_at": interview.scheduled_at.isoformat(),
            "interview_type": interview.interview_type,
        },
    )
    db.add(log)
    
    await db.commit()
    await db.refresh(db_interview)
    
    return InterviewResponse.model_validate(db_interview)


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get interview details."""
    result = await db.execute(
        select(Interview)
        .where(Interview.id == interview_id)
        .where(Interview.user_id == current_user.id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found."
        )
    
    return InterviewResponse.model_validate(interview)


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: str,
    update: InterviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an interview."""
    result = await db.execute(
        select(Interview)
        .where(Interview.id == interview_id)
        .where(Interview.user_id == current_user.id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found."
        )
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview, field, value)
    
    interview.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(interview)
    
    return InterviewResponse.model_validate(interview)


@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel/delete an interview."""
    result = await db.execute(
        select(Interview)
        .where(Interview.id == interview_id)
        .where(Interview.user_id == current_user.id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found."
        )
    
    interview.status = "canceled"
    interview.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Interview canceled."}


@router.post("/{interview_id}/complete", response_model=InterviewResponse)
async def complete_interview(
    interview_id: str,
    feedback: Optional[str] = None,
    rating: Optional[int] = Query(None, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark interview as completed with feedback."""
    result = await db.execute(
        select(Interview)
        .where(Interview.id == interview_id)
        .where(Interview.user_id == current_user.id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found."
        )
    
    interview.status = "completed"
    interview.feedback = feedback
    interview.rating = rating
    interview.updated_at = datetime.utcnow()
    
    # Log activity
    log = ActivityLog(
        id=uuid4(),
        user_id=current_user.id,
        action="interview_completed",
        entity_type="candidate",
        entity_id=interview.candidate_id,
        details={
            "interview_id": str(interview_id),
            "rating": rating,
        },
    )
    db.add(log)
    
    await db.commit()
    await db.refresh(interview)
    
    return InterviewResponse.model_validate(interview)
