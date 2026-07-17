from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models import User, JobPosition, ActivityLog
from app.schemas import (
    JobPositionCreate,
    JobPositionUpdate,
    JobPositionResponse,
    JobPositionListResponse,
    MessageResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/jobs", tags=["Job Positions"])


@router.get("", response_model=JobPositionListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all job positions with pagination and filters."""
    query = select(JobPosition).where(JobPosition.user_id == current_user.id)
    count_query = select(func.count(JobPosition.id)).where(JobPosition.user_id == current_user.id)
    
    # Apply filters
    if search:
        search_filter = or_(
            JobPosition.title.ilike(f"%{search}%"),
            JobPosition.description.ilike(f"%{search}%"),
            JobPosition.location.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    if status:
        query = query.where(JobPosition.status == status)
        count_query = count_query.where(JobPosition.status == status)
    
    if department:
        query = query.where(JobPosition.department == department)
        count_query = count_query.where(JobPosition.department == department)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(JobPosition.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return JobPositionListResponse(
        items=jobs,
        total=total
    )


@router.post("", response_model=JobPositionResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobPositionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new job position."""
    job = JobPosition(
        user_id=current_user.id,
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements or {},
        department=job_data.department,
        location=job_data.location,
        salary_range=job_data.salary_range,
        status=job_data.status or "open",
    )
    
    db.add(job)
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="job_created",
        entity_type="job_position",
        entity_id=job.id,
        details={"title": job.title}
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(job)
    
    return job


@router.get("/{job_id}", response_model=JobPositionResponse)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a job position by ID."""
    result = await db.execute(
        select(JobPosition).where(
            JobPosition.id == job_id,
            JobPosition.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found"
        )
    
    return job


@router.put("/{job_id}", response_model=JobPositionResponse)
async def update_job(
    job_id: uuid.UUID,
    job_data: JobPositionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a job position."""
    result = await db.execute(
        select(JobPosition).where(
            JobPosition.id == job_id,
            JobPosition.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found"
        )
    
    # Update fields
    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    job.updated_at = datetime.utcnow()
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="job_updated",
        entity_type="job_position",
        entity_id=job.id,
        details={"fields": list(update_data.keys())}
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(job)
    
    return job


@router.delete("/{job_id}", response_model=MessageResponse)
async def delete_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a job position."""
    result = await db.execute(
        select(JobPosition).where(
            JobPosition.id == job_id,
            JobPosition.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found"
        )
    
    # Log activity before deletion
    activity = ActivityLog(
        user_id=current_user.id,
        action="job_deleted",
        entity_type="job_position",
        entity_id=job.id,
        details={"title": job.title}
    )
    db.add(activity)
    
    await db.delete(job)
    await db.commit()
    
    return MessageResponse(message="Job position deleted successfully")


@router.put("/{job_id}/status", response_model=JobPositionResponse)
async def update_job_status(
    job_id: uuid.UUID,
    status_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update job position status."""
    result = await db.execute(
        select(JobPosition).where(
            JobPosition.id == job_id,
            JobPosition.user_id == current_user.id
        )
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job position not found"
        )
    
    new_status = status_data.get("status")
    if new_status not in ["open", "closed", "on_hold"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be 'open', 'closed', or 'on_hold'"
        )
    
    old_status = job.status
    job.status = new_status
    job.updated_at = datetime.utcnow()
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="job_status_changed",
        entity_type="job_position",
        entity_id=job.id,
        details={
            "old_status": old_status,
            "new_status": new_status,
            "job_title": job.title
        }
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(job)
    
    return job
