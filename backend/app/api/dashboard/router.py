from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models import User, Candidate, JobPosition, SentEmail, ActivityLog
from app.schemas import (
    DashboardOverview,
    DashboardPipeline,
    PipelineStage,
    HiringMetrics,
    DashboardActivity,
    ActivityItem,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverview)
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard overview statistics."""
    # Total candidates
    total_candidates_result = await db.execute(
        select(func.count(Candidate.id)).where(Candidate.user_id == current_user.id)
    )
    total_candidates = total_candidates_result.scalar()
    
    # Active candidates (not rejected)
    active_candidates_result = await db.execute(
        select(func.count(Candidate.id)).where(
            Candidate.user_id == current_user.id,
            Candidate.status != "rejected"
        )
    )
    active_candidates = active_candidates_result.scalar()
    
    # Total jobs
    total_jobs_result = await db.execute(
        select(func.count(JobPosition.id)).where(JobPosition.user_id == current_user.id)
    )
    total_jobs = total_jobs_result.scalar()
    
    # Open jobs
    open_jobs_result = await db.execute(
        select(func.count(JobPosition.id)).where(
            JobPosition.user_id == current_user.id,
            JobPosition.status == "open"
        )
    )
    open_jobs = open_jobs_result.scalar()
    
    # Total emails sent
    total_emails_result = await db.execute(
        select(func.count(SentEmail.id)).where(
            SentEmail.user_id == current_user.id,
            SentEmail.status.in_(["sent", "delivered", "opened", "replied"])
        )
    )
    total_emails_sent = total_emails_result.scalar()
    
    # Email open rate
    total_delivered_result = await db.execute(
        select(func.count(SentEmail.id)).where(
            SentEmail.user_id == current_user.id,
            SentEmail.status.in_(["delivered", "opened", "replied"])
        )
    )
    total_delivered = total_delivered_result.scalar()
    
    total_opened_result = await db.execute(
        select(func.count(SentEmail.id)).where(
            SentEmail.user_id == current_user.id,
            SentEmail.status.in_(["opened", "replied"])
        )
    )
    total_opened = total_opened_result.scalar()
    
    email_open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
    
    return DashboardOverview(
        total_candidates=total_candidates,
        active_candidates=active_candidates,
        total_jobs=total_jobs,
        open_jobs=open_jobs,
        total_emails_sent=total_emails_sent,
        email_open_rate=round(email_open_rate, 2),
    )


@router.get("/pipeline", response_model=DashboardPipeline)
async def get_pipeline(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get candidate pipeline breakdown."""
    # Status labels
    status_labels = {
        "new": "New Applications",
        "screening": "Screening",
        "interview": "Interview",
        "offer": "Offer",
        "hired": "Hired",
        "rejected": "Rejected",
    }
    
    stages = []
    total = 0
    
    for status, label in status_labels.items():
        count_result = await db.execute(
            select(func.count(Candidate.id)).where(
                Candidate.user_id == current_user.id,
                Candidate.status == status
            )
        )
        count = count_result.scalar()
        total += count
        stages.append(PipelineStage(
            status=status,
            count=count,
            label=label
        ))
    
    return DashboardPipeline(stages=stages, total=total)


@router.get("/metrics", response_model=HiringMetrics)
async def get_metrics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get hiring metrics for the specified period."""
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Candidates hired
    hired_result = await db.execute(
        select(func.count(Candidate.id)).where(
            Candidate.user_id == current_user.id,
            Candidate.status == "hired"
        )
    )
    total_hired = hired_result.scalar()
    
    # Candidates rejected
    rejected_result = await db.execute(
        select(func.count(Candidate.id)).where(
            Candidate.user_id == current_user.id,
            Candidate.status == "rejected"
        )
    )
    total_rejected = rejected_result.scalar()
    
    # Calculate offer acceptance rate
    total_offers = total_hired + total_rejected
    offer_acceptance_rate = (total_hired / total_offers * 100) if total_offers > 0 else 0
    
    # Average candidates per position
    positions_result = await db.execute(
        select(func.count(JobPosition.id)).where(
            JobPosition.user_id == current_user.id,
            JobPosition.status == "open"
        )
    )
    open_positions = positions_result.scalar()
    
    avg_candidates_per_position = (total_hired / open_positions) if open_positions > 0 else 0
    
    # Time to hire (simplified - in production would calculate from actual hire dates)
    avg_time_to_hire = 21.5  # Placeholder - would need hire date tracking
    
    return HiringMetrics(
        avg_time_to_hire=avg_time_to_hire,
        total_hired=total_hired,
        total_rejected=total_rejected,
        offer_acceptance_rate=round(offer_acceptance_rate, 2),
        candidates_per_position=round(avg_candidates_per_position, 2),
    )


@router.get("/activity", response_model=DashboardActivity)
async def get_activity(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    entity_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent activity logs."""
    query = select(ActivityLog).where(ActivityLog.user_id == current_user.id)
    count_query = select(func.count(ActivityLog.id)).where(ActivityLog.user_id == current_user.id)
    
    if entity_type:
        query = query.where(ActivityLog.entity_type == entity_type)
        count_query = count_query.where(ActivityLog.entity_type == entity_type)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(ActivityLog.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    activities = result.scalars().all()
    
    return DashboardActivity(
        items=activities,
        total=total
    )


@router.get("/chart/candidates-over-time", response_model=dict)
async def get_candidates_over_time(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get candidate creation data over time for charts."""
    from datetime import datetime, timedelta
    
    # For simplicity, we'll return mock data
    # In production, you'd query the database with date grouping
    current_date = datetime.utcnow()
    data = []
    
    for i in range(days):
        date = current_date - timedelta(days=i)
        # Mock data - in production calculate actual counts per day
        count = (i % 7) + 1  # Simulated daily counts
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count
        })
    
    data.reverse()  # Chronological order
    
    return {"data": data, "period_days": days}


@router.get("/chart/email-performance", response_model=dict)
async def get_email_performance(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get email performance data over time."""
    from datetime import datetime, timedelta
    
    # Mock data - in production calculate actual metrics per day
    current_date = datetime.utcnow()
    data = []
    
    for i in range(days):
        date = current_date - timedelta(days=i)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "sent": (i % 5) + 1,
            "delivered": (i % 4) + 1,
            "opened": (i % 3),
            "replied": (i % 2)
        })
    
    data.reverse()
    
    return {"data": data, "period_days": days}
