import os
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.models import User, Candidate, ActivityLog
from app.schemas import (
    CandidateCreate,
    CandidateUpdate,
    CandidateStatusUpdate,
    CandidateResponse,
    CandidateListResponse,
    ResumeUploadResponse,
    MessageResponse,
)
from app.api.deps import get_current_user
from app.utils import (
    extract_text_from_pdf,
    parse_resume_text,
    generate_filename,
    validate_file_type,
)

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get("", response_model=CandidateListResponse)
async def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    skills: Optional[str] = None,
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all candidates with pagination and filters."""
    query = select(Candidate).where(Candidate.user_id == current_user.id)
    count_query = select(func.count(Candidate.id)).where(Candidate.user_id == current_user.id)
    
    # Apply filters
    if search:
        search_filter = or_(
            Candidate.full_name.ilike(f"%{search}%"),
            Candidate.email.ilike(f"%{search}%"),
            Candidate.current_position.ilike(f"%{search}%"),
            Candidate.current_company.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    if status:
        query = query.where(Candidate.status == status)
        count_query = count_query.where(Candidate.status == status)
    
    if source:
        query = query.where(Candidate.source == source)
        count_query = count_query.where(Candidate.source == source)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Candidate.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    candidates = result.scalars().all()
    
    return CandidateListResponse(
        items=candidates,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new candidate."""
    candidate = Candidate(
        user_id=current_user.id,
        full_name=candidate_data.full_name,
        email=candidate_data.email,
        phone=candidate_data.phone,
        skills=candidate_data.skills or [],
        experience_years=candidate_data.experience_years or 0,
        education_level=candidate_data.education_level,
        current_position=candidate_data.current_position,
        current_company=candidate_data.current_company,
        linkedin_url=candidate_data.linkedin_url,
        status=candidate_data.status or "new",
        source=candidate_data.source,
        notes=candidate_data.notes,
        resume_text=candidate_data.resume_text,
    )
    
    db.add(candidate)
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="candidate_created",
        entity_type="candidate",
        entity_id=candidate.id,
        details={"name": candidate.full_name, "email": candidate.email}
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(candidate)
    
    return candidate


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a candidate by ID."""
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.user_id == current_user.id
        )
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: uuid.UUID,
    candidate_data: CandidateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a candidate."""
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.user_id == current_user.id
        )
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Update fields
    update_data = candidate_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)
    
    candidate.updated_at = datetime.utcnow()
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="candidate_updated",
        entity_type="candidate",
        entity_id=candidate.id,
        details={"fields": list(update_data.keys())}
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(candidate)
    
    return candidate


@router.delete("/{candidate_id}", response_model=MessageResponse)
async def delete_candidate(
    candidate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a candidate."""
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.user_id == current_user.id
        )
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Log activity before deletion
    activity = ActivityLog(
        user_id=current_user.id,
        action="candidate_deleted",
        entity_type="candidate",
        entity_id=candidate.id,
        details={"name": candidate.full_name, "email": candidate.email}
    )
    db.add(activity)
    
    await db.delete(candidate)
    await db.commit()
    
    return MessageResponse(message="Candidate deleted successfully")


@router.put("/{candidate_id}/status", response_model=CandidateResponse)
async def update_candidate_status(
    candidate_id: uuid.UUID,
    status_data: CandidateStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update candidate status."""
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.user_id == current_user.id
        )
    )
    candidate = result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    old_status = candidate.status
    candidate.status = status_data.status
    candidate.updated_at = datetime.utcnow()
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="candidate_status_changed",
        entity_type="candidate",
        entity_id=candidate.id,
        details={
            "old_status": old_status,
            "new_status": status_data.status,
            "candidate_name": candidate.full_name
        }
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(candidate)
    
    return candidate


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse a resume PDF."""
    # Validate file type
    if not validate_file_type(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Validate file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR) / str(current_user.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    filename = generate_filename(file.filename, str(current_user.id))
    file_path = upload_dir / filename.split('/')[-1]
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Extract text from PDF
    try:
        resume_text = extract_text_from_pdf(str(file_path))
    except Exception as e:
        # Clean up file if extraction fails
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )
    
    # Parse resume
    extracted_data = parse_resume_text(resume_text)
    
    # Generate URL
    resume_url = f"/uploads/{current_user.id}/{filename.split('/')[-1]}"
    
    return ResumeUploadResponse(
        resume_url=resume_url,
        resume_text=resume_text,
        extracted_data=extracted_data
    )


@router.post("/parse", response_model=dict)
async def parse_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Parse a resume PDF and extract candidate information."""
    # Validate file type
    if not validate_file_type(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Read file content
    content = await file.read()
    
    # Create temp file for parsing
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Extract text
        resume_text = extract_text_from_pdf(tmp_path)
        
        # Parse resume
        extracted_data = parse_resume_text(resume_text)
        
        return {
            "resume_text": resume_text,
            "extracted_data": extracted_data
        }
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
