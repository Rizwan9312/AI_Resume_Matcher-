"""Rewriter API endpoints."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db_session
from app.models.rewrite_session import RewriteSession, RewriteStatus
from app.models.match_result import MatchResult
from app.models.job_description import JobDescription
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.rewriter import RewriteResponse
from pydantic import BaseModel
from app.workers.rewrite_tasks import run_full_rewrite_pipeline

router = APIRouter(prefix="/rewrites", tags=["Rewrites"])

class RewriteRequest(BaseModel):
    match_id: uuid.UUID

@router.post("", response_model=RewriteResponse, status_code=status.HTTP_201_CREATED)
async def create_rewrite_session(
    req: RewriteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Start a full resume rewrite based on a previous match."""
    
    # 1. Fetch the match
    match_result = await db.execute(
        select(MatchResult).where(MatchResult.id == req.match_id)
    )
    match_obj = match_result.scalar_one_or_none()
    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")
    if match_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this match")

    # 2. Fetch the job description text
    jd_result = await db.execute(
        select(JobDescription).where(JobDescription.id == match_obj.job_id)
    )
    job_obj = jd_result.scalar_one_or_none()
    if not job_obj:
        raise HTTPException(status_code=404, detail="Job description not found")

    jd_text = job_obj.raw_text

    # 3. Create the RewriteSession
    session = RewriteSession(
        user_id=match_obj.user_id,
        resume_id=match_obj.resume_id,
        jd_text=jd_text,
        match_id=req.match_id,
        status=RewriteStatus.PENDING,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # 4. Trigger the celery task
    run_full_rewrite_pipeline.delay(str(session.id))

    return session

@router.get("/{session_id}", response_model=RewriteResponse)
async def get_rewrite_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get the status and result of a rewrite session."""
    result = await db.execute(
        select(RewriteSession).where(RewriteSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Rewrite session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
        
    return session