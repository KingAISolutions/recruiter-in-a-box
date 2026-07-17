from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models import User, Candidate, JobPosition, CandidateScore, ActivityLog
from app.schemas import (
    ScoreRequest,
    BulkScoreRequest,
    ScoreResponse,
    MessageResponse,
)
from app.api.deps import get_current_user
from app.services import ai_service

router = APIRouter(prefix="/scoring", tags=["AI Scoring"])


@router.post("/candidate/{candidate_id}", response_model=ScoreResponse)
async def score_candidate(
    candidate_id: uuid.UUID,
    job_position_id: uuid.UUID = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Score a single candidate against job requirements."""
    # Get candidate
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
    
    # Get job requirements if job_id provided
    job_requirements = None
    if job_position_id:
        job_result = await db.execute(
            select(JobPosition).where(
                JobPosition.id == job_position_id,
                JobPosition.user_id == current_user.id
            )
        )
        job = job_result.scalar_one_or_none()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job position not found"
            )
        job_requirements = job.requirements
    
    # Score candidate using AI service
    candidate_data = {
        "full_name": candidate.full_name,
        "email": candidate.email,
        "skills": candidate.skills or [],
        "experience_years": candidate.experience_years or 0,
        "education_level": candidate.education_level,
        "current_position": candidate.current_position,
        "current_company": candidate.current_company,
    }
    
    score_result = await ai_service.score_candidate(candidate_data, job_requirements)
    
    # Check for existing score
    existing_score_result = await db.execute(
        select(CandidateScore).where(
            CandidateScore.candidate_id == candidate_id,
            CandidateScore.job_position_id == job_position_id
        )
    )
    existing_score = existing_score_result.scalar_one_or_none()
    
    if existing_score:
        # Update existing score
        existing_score.skills_score = score_result["skills_score"]
        existing_score.experience_score = score_result["experience_score"]
        existing_score.education_score = score_result["education_score"]
        existing_score.overall_score = score_result["overall_score"]
        existing_score.breakdown = score_result["breakdown"]
        existing_score.updated_at = datetime.utcnow()
        score_record = existing_score
    else:
        # Create new score
        score_record = CandidateScore(
            candidate_id=candidate_id,
            job_position_id=job_position_id,
            skills_score=score_result["skills_score"],
            experience_score=score_result["experience_score"],
            education_score=score_result["education_score"],
            overall_score=score_result["overall_score"],
            breakdown=score_result["breakdown"],
        )
        db.add(score_record)
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="candidate_scored",
        entity_type="candidate_score",
        entity_id=score_record.id,
        details={
            "candidate_name": candidate.full_name,
            "overall_score": score_result["overall_score"],
            "job_position_id": str(job_position_id) if job_position_id else None
        }
    )
    db.add(activity)
    
    await db.commit()
    await db.refresh(score_record)
    
    return score_record


@router.post("/bulk", response_model=List[ScoreResponse])
async def bulk_score_candidates(
    bulk_data: BulkScoreRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Score multiple candidates against job requirements."""
    # Get job requirements if job_id provided
    job_requirements = None
    if bulk_data.job_position_id:
        job_result = await db.execute(
            select(JobPosition).where(
                JobPosition.id == bulk_data.job_position_id,
                JobPosition.user_id == current_user.id
            )
        )
        job = job_result.scalar_one_or_none()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job position not found"
            )
        job_requirements = job.requirements
    
    scored_candidates = []
    
    for candidate_id in bulk_data.candidate_ids:
        # Get candidate
        result = await db.execute(
            select(Candidate).where(
                Candidate.id == candidate_id,
                Candidate.user_id == current_user.id
            )
        )
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            continue
        
        # Score candidate
        candidate_data = {
            "full_name": candidate.full_name,
            "email": candidate.email,
            "skills": candidate.skills or [],
            "experience_years": candidate.experience_years or 0,
            "education_level": candidate.education_level,
            "current_position": candidate.current_position,
            "current_company": candidate.current_company,
        }
        
        score_result = await ai_service.score_candidate(candidate_data, job_requirements)
        
        # Check for existing score
        existing_score_result = await db.execute(
            select(CandidateScore).where(
                CandidateScore.candidate_id == candidate_id,
                CandidateScore.job_position_id == bulk_data.job_position_id
            )
        )
        existing_score = existing_score_result.scalar_one_or_none()
        
        if existing_score:
            existing_score.skills_score = score_result["skills_score"]
            existing_score.experience_score = score_result["experience_score"]
            existing_score.education_score = score_result["education_score"]
            existing_score.overall_score = score_result["overall_score"]
            existing_score.breakdown = score_result["breakdown"]
            existing_score.updated_at = datetime.utcnow()
            scored_candidates.append(existing_score)
        else:
            score_record = CandidateScore(
                candidate_id=candidate_id,
                job_position_id=bulk_data.job_position_id,
                skills_score=score_result["skills_score"],
                experience_score=score_result["experience_score"],
                education_score=score_result["education_score"],
                overall_score=score_result["overall_score"],
                breakdown=score_result["breakdown"],
            )
            db.add(score_record)
            scored_candidates.append(score_record)
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="bulk_candidates_scored",
        entity_type="candidate_score",
        entity_id=None,
        details={
            "count": len(scored_candidates),
            "job_position_id": str(bulk_data.job_position_id) if bulk_data.job_position_id else None
        }
    )
    db.add(activity)
    
    await db.commit()
    
    # Refresh all scores
    for score in scored_candidates:
        await db.refresh(score)
    
    return scored_candidates


@router.get("/{candidate_id}/history", response_model=List[ScoreResponse])
async def get_scoring_history(
    candidate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get scoring history for a candidate."""
    # Verify candidate belongs to user
    candidate_result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.user_id == current_user.id
        )
    )
    candidate = candidate_result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Get all scores
    result = await db.execute(
        select(CandidateScore)
        .where(CandidateScore.candidate_id == candidate_id)
        .order_by(CandidateScore.created_at.desc())
    )
    scores = result.scalars().all()
    
    return scores


@router.get("/{candidate_id}/latest", response_model=ScoreResponse)
async def get_latest_score(
    candidate_id: uuid.UUID,
    job_position_id: uuid.UUID = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the latest score for a candidate."""
    # Verify candidate belongs to user
    candidate_result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.user_id == current_user.id
        )
    )
    candidate = candidate_result.scalar_one_or_none()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Build query for latest score
    query = select(CandidateScore).where(CandidateScore.candidate_id == candidate_id)
    if job_position_id:
        query = query.where(CandidateScore.job_position_id == job_position_id)
    query = query.order_by(CandidateScore.created_at.desc()).limit(1)
    
    result = await db.execute(query)
    score = result.scalar_one_or_none()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No score found for this candidate"
        )
    
    return score
