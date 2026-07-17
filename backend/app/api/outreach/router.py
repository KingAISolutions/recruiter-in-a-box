from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models import User, Candidate, JobPosition, EmailTemplate, SentEmail, ActivityLog
from app.schemas import (
    SendEmailRequest,
    BulkEmailRequest,
    SentEmailResponse,
    EmailStatsResponse,
    MessageResponse,
)
from app.api.deps import get_current_user
from app.utils import interpolate_template
from app.services import ai_service

router = APIRouter(prefix="/outreach", tags=["Outreach"])


@router.post("/send", response_model=SentEmailResponse)
async def send_email(
    email_data: SendEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a single email to a candidate."""
    # Get candidate
    candidate_result = await db.execute(
        select(Candidate).where(
            Candidate.id == email_data.candidate_id,
            Candidate.user_id == current_user.id
        )
    )
    candidate = candidate_result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Get template if provided
    template = None
    subject = email_data.subject or ""
    body = email_data.body or ""
    
    if email_data.template_id:
        template_result = await db.execute(
            select(EmailTemplate).where(
                EmailTemplate.id == email_data.template_id,
                EmailTemplate.user_id == current_user.id
            )
        )
        template = template_result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        subject = template.subject
        body = template.body
    
    # Get job position for context
    job_position = None
    if email_data.job_position_id:
        job_result = await db.execute(
            select(JobPosition).where(
                JobPosition.id == email_data.job_position_id,
                JobPosition.user_id == current_user.id
            )
        )
        job_position = job_result.scalar_one_or_none()
    
    # Prepare variables for interpolation
    variables = {
        "candidate_name": candidate.full_name,
        "first_name": candidate.full_name.split()[0] if candidate.full_name else "there",
        "email": candidate.email,
        "position": job_position.title if job_position else "",
        "company_name": current_user.company_name or "our company",
        "job_title": job_position.title if job_position else "",
        "department": job_position.department if job_position else "",
        "location": job_position.location if job_position else "",
    }
    
    # Interpolate template variables
    if template:
        subject = interpolate_template(template.subject, variables)
        body = interpolate_template(template.body, variables)
    
    # Create sent email record
    sent_email = SentEmail(
        user_id=current_user.id,
        candidate_id=candidate.id,
        template_id=email_data.template_id,
        job_position_id=email_data.job_position_id,
        subject=subject,
        body=body,
        status="sent",
        sent_at=datetime.utcnow(),
    )
    
    db.add(sent_email)
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="email_sent",
        entity_type="sent_email",
        entity_id=sent_email.id,
        details={
            "candidate_name": candidate.full_name,
            "subject": subject[:50],
            "status": "sent"
        }
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(sent_email)
    
    # Simulate email delivery (in production, integrate with email service)
    sent_email.status = "delivered"
    sent_email.delivered_at = datetime.utcnow()
    await db.commit()
    await db.refresh(sent_email)
    
    return sent_email


@router.post("/bulk", response_model=List[SentEmailResponse])
async def bulk_send_emails(
    bulk_data: BulkEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send emails to multiple candidates."""
    # Get template if provided
    template = None
    if bulk_data.template_id:
        template_result = await db.execute(
            select(EmailTemplate).where(
                EmailTemplate.id == bulk_data.template_id,
                EmailTemplate.user_id == current_user.id
            )
        )
        template = template_result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
    
    # Get job position for context
    job_position = None
    if bulk_data.job_position_id:
        job_result = await db.execute(
            select(JobPosition).where(
                JobPosition.id == bulk_data.job_position_id,
                JobPosition.user_id == current_user.id
            )
        )
        job_position = job_result.scalar_one_or_none()
    
    sent_emails = []
    
    for candidate_id in bulk_data.candidate_ids:
        # Get candidate
        candidate_result = await db.execute(
            select(Candidate).where(
                Candidate.id == candidate_id,
                Candidate.user_id == current_user.id
            )
        )
        candidate = candidate_result.scalar_one_or_none()
        
        if not candidate:
            continue
        
        # Prepare variables
        variables = {
            "candidate_name": candidate.full_name,
            "first_name": candidate.full_name.split()[0] if candidate.full_name else "there",
            "email": candidate.email,
            "position": job_position.title if job_position else "",
            "company_name": current_user.company_name or "our company",
            "job_title": job_position.title if job_position else "",
            "department": job_position.department if job_position else "",
            "location": job_position.location if job_position else "",
        }
        
        # Get subject and body
        subject = template.subject if template else "Regarding Your Application"
        body = template.body if template else "Dear {candidate_name},\n\nWe would like to connect with you regarding an opportunity at {company_name}.\n\nBest regards"
        
        # Interpolate
        if template:
            subject = interpolate_template(template.subject, variables)
            body = interpolate_template(template.body, variables)
        
        # Create sent email record
        sent_email = SentEmail(
            user_id=current_user.id,
            candidate_id=candidate.id,
            template_id=bulk_data.template_id,
            job_position_id=bulk_data.job_position_id,
            subject=subject,
            body=body,
            status="sent",
            sent_at=datetime.utcnow(),
        )
        
        db.add(sent_email)
        sent_emails.append(sent_email)
    
    # Log bulk activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="bulk_emails_sent",
        entity_type="sent_email",
        entity_id=None,
        details={
            "count": len(sent_emails),
            "template_id": str(bulk_data.template_id) if bulk_data.template_id else None,
            "job_position_id": str(bulk_data.job_position_id) if bulk_data.job_position_id else None
        }
    )
    db.add(activity)
    
    await db.commit()
    
    # Simulate delivery for all emails
    for email in sent_emails:
        email.status = "delivered"
        email.delivered_at = datetime.utcnow()
    
    await db.commit()
    
    # Refresh all emails
    for email in sent_emails:
        await db.refresh(email)
    
    return sent_emails


@router.get("/emails", response_model=dict)
async def list_sent_emails(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    candidate_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all sent emails with pagination and filters."""
    query = select(SentEmail).where(SentEmail.user_id == current_user.id)
    count_query = select(func.count(SentEmail.id)).where(SentEmail.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.where(SentEmail.status == status)
        count_query = count_query.where(SentEmail.status == status)
    
    if candidate_id:
        query = query.where(SentEmail.candidate_id == candidate_id)
        count_query = count_query.where(SentEmail.candidate_id == candidate_id)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(SentEmail.sent_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    emails = result.scalars().all()
    
    return {
        "items": emails,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/emails/{email_id}", response_model=SentEmailResponse)
async def get_sent_email(
    email_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a sent email by ID."""
    result = await db.execute(
        select(SentEmail).where(
            SentEmail.id == email_id,
            SentEmail.user_id == current_user.id
        )
    )
    email = result.scalar_one_or_none()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return email


@router.get("/stats", response_model=EmailStatsResponse)
async def get_email_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get email statistics."""
    # Total sent
    total_result = await db.execute(
        select(func.count(SentEmail.id)).where(
            SentEmail.user_id == current_user.id,
            SentEmail.status.in_(["sent", "delivered", "opened", "replied"])
        )
    )
    total_sent = total_result.scalar()
    
    # Total delivered
    delivered_result = await db.execute(
        select(func.count(SentEmail.id)).where(
            SentEmail.user_id == current_user.id,
            SentEmail.status.in_(["delivered", "opened", "replied"])
        )
    )
    total_delivered = delivered_result.scalar()
    
    # Total opened
    opened_result = await db.execute(
        select(func.count(SentEmail.id)).where(
            SentEmail.user_id == current_user.id,
            SentEmail.status.in_(["opened", "replied"])
        )
    )
    total_opened = opened_result.scalar()
    
    # Total replied
    replied_result = await db.execute(
        select(func.count(SentEmail.id)).where(
            SentEmail.user_id == current_user.id,
            SentEmail.status == "replied"
        )
    )
    total_replied = replied_result.scalar()
    
    # Total failed
    failed_result = await db.execute(
        select(func.count(SentEmail.id)).where(
            SentEmail.user_id == current_user.id,
            SentEmail.status == "failed"
        )
    )
    total_failed = failed_result.scalar()
    
    # Calculate rates
    delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
    open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
    reply_rate = (total_replied / total_delivered * 100) if total_delivered > 0 else 0
    
    return EmailStatsResponse(
        total_sent=total_sent,
        total_delivered=total_delivered,
        total_opened=total_opened,
        total_replied=total_replied,
        total_failed=total_failed,
        delivery_rate=round(delivery_rate, 2),
        open_rate=round(open_rate, 2),
        reply_rate=round(reply_rate, 2),
    )


@router.post("/emails/{email_id}/track-open", response_model=MessageResponse)
async def track_email_open(
    email_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Track an email open (called by tracking pixel)."""
    result = await db.execute(
        select(SentEmail).where(SentEmail.id == email_id)
    )
    email = result.scalar_one_or_none()
    
    if email and not email.opened_at:
        email.status = "opened"
        email.opened_at = datetime.utcnow()
        await db.commit()
    
    # Return 1x1 transparent GIF
    from fastapi.responses import Response
    import base64
    
    # 1x1 transparent GIF
    gif = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    return Response(content=gif, media_type="image/gif")
