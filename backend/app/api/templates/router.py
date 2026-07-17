from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models import User, EmailTemplate, ActivityLog
from app.schemas import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    MessageResponse,
)
from app.api.deps import get_current_user
from app.utils import parse_template_variables

router = APIRouter(prefix="/templates", tags=["Email Templates"])


@router.get("", response_model=dict)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all email templates with pagination."""
    query = select(EmailTemplate).where(EmailTemplate.user_id == current_user.id)
    count_query = select(func.count(EmailTemplate.id)).where(EmailTemplate.user_id == current_user.id)
    
    # Apply search filter
    if search:
        search_filter = or_(
            EmailTemplate.name.ilike(f"%{search}%"),
            EmailTemplate.subject.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(EmailTemplate.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    templates = result.scalars().all()
    
    return {
        "items": templates,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: EmailTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new email template."""
    # Extract variables from body if not provided
    variables = template_data.variables
    if not variables:
        variables = parse_template_variables(template_data.body)
    
    template = EmailTemplate(
        user_id=current_user.id,
        name=template_data.name,
        subject=template_data.subject,
        body=template_data.body,
        variables=variables,
    )
    
    db.add(template)
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="template_created",
        entity_type="email_template",
        entity_id=template.id,
        details={"name": template.name}
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.get("/{template_id}", response_model=EmailTemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get an email template by ID."""
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == template_id,
            EmailTemplate.user_id == current_user.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template


@router.put("/{template_id}", response_model=EmailTemplateResponse)
async def update_template(
    template_id: uuid.UUID,
    template_data: EmailTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an email template."""
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == template_id,
            EmailTemplate.user_id == current_user.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Update fields
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    # Re-extract variables if body was updated
    if template_data.body:
        template.variables = parse_template_variables(template.body)
    
    template.updated_at = datetime.utcnow()
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="template_updated",
        entity_type="email_template",
        entity_id=template.id,
        details={"fields": list(update_data.keys())}
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(template)
    
    return template


@router.delete("/{template_id}", response_model=MessageResponse)
async def delete_template(
    template_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an email template."""
    result = await db.execute(
        select(EmailTemplate).where(
            EmailTemplate.id == template_id,
            EmailTemplate.user_id == current_user.id
        )
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Log activity before deletion
    activity = ActivityLog(
        user_id=current_user.id,
        action="template_deleted",
        entity_type="email_template",
        entity_id=template.id,
        details={"name": template.name}
    )
    db.add(activity)
    
    await db.delete(template)
    await db.commit()
    
    return MessageResponse(message="Template deleted successfully")


@router.post("/preview", response_model=dict)
async def preview_template(
    template_data: EmailTemplateCreate,
    variables: dict,
    current_user: User = Depends(get_current_user)
):
    """Preview a template with provided variables."""
    from app.utils import interpolate_template
    
    # Interpolate variables
    preview_subject = interpolate_template(template_data.subject, variables)
    preview_body = interpolate_template(template_data.body, variables)
    
    # Extract detected variables
    detected_variables = parse_template_variables(template_data.body)
    
    return {
        "subject": preview_subject,
        "body": preview_body,
        "detected_variables": detected_variables,
        "provided_variables": list(variables.keys())
    }
