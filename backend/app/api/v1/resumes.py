"""Resume API routes — upload, list, get, delete."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.resume import ParseStatus, Resume
from app.models.match_result import MatchResult
from app.models.job_description import JobDescription
from app.models.user import User
from app.schemas.resume import ResumeListResponse, ResumeResponse
from app.utils.file_utils import (
    MAX_FILE_SIZE,
    generate_s3_key,
    get_mime_type,
    upload_file,
    validate_file_extension,
    validate_magic_bytes,
)
from app.utils.logger import get_logger
from pydantic import BaseModel
from datetime import datetime
import uuid

class ResumeHistoryItem(BaseModel):
    match_id: uuid.UUID
    final_score: float | None
    status: str
    created_at: datetime
    job_title: str | None

class ResumeHistoryResponse(BaseModel):
    history: list[ResumeHistoryItem]

class ResumeVersionItem(BaseModel):
    id: uuid.UUID
    version_number: int
    is_active: bool
    created_at: datetime
    best_score: float | None

class ResumeVersionResponse(BaseModel):
    versions: list[ResumeVersionItem]

logger = get_logger("resumes_api")

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Upload a resume file (PDF or DOCX, max 10MB)."""
    if not file.filename:
        raise HTTPException(400, detail={"code": "invalid_file", "message": "No file provided"})

    ext = validate_file_extension(file.filename)
    if ext is None:
        raise HTTPException(400, detail={"code": "invalid_file_type", "message": "Only PDF and DOCX allowed"})

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, detail={"code": "file_too_large", "message": f"Max {MAX_FILE_SIZE // (1024*1024)}MB"})

    if not validate_magic_bytes(content, ext):
        logger.warning("file.rejected", filename=file.filename, reason="magic_byte_mismatch")
        raise HTTPException(422, detail={"code": "magic_byte_mismatch", "message": "File content doesn't match extension"})

    s3_key = generate_s3_key(str(current_user.id), file.filename)
    await upload_file(content, s3_key)

    # Check for existing resume with the same filename to handle versions
    existing_result = await session.execute(
        select(Resume).where(
            Resume.user_id == current_user.id,
            Resume.filename == file.filename,
            Resume.deleted_at.is_(None)
        ).order_by(Resume.version_number.desc())
    )
    existing_resumes = existing_result.scalars().all()
    
    version_number = 1
    parent_resume_id = None
    
    if existing_resumes:
        latest_resume = existing_resumes[0]
        version_number = latest_resume.version_number + 1
        parent_resume_id = latest_resume.parent_resume_id or latest_resume.id
        
        # Deactivate older versions
        for r in existing_resumes:
            r.is_active = False

    resume = Resume(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        filename=file.filename,
        s3_key=s3_key,
        file_size_bytes=len(content),
        mime_type=get_mime_type(ext),
        parse_status=ParseStatus.PENDING,
        version_number=version_number,
        parent_resume_id=parent_resume_id,
        is_active=True,
    )
    session.add(resume)
    await session.commit()      # ← changed from flush() to commit()
    await session.refresh(resume)  # ← reload DB-generated fields

    logger.info("file.upload", resume_id=str(resume.id), size=len(content))
    return ResumeResponse.model_validate(resume)


@router.get("", response_model=ResumeListResponse)
async def list_resumes(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """List all resumes for the current user."""
    result = await session.execute(
        select(Resume).where(
            Resume.user_id == current_user.id,
            Resume.deleted_at.is_(None),
        ).order_by(Resume.created_at.desc())
    )
    resumes = result.scalars().all()
    return ResumeListResponse(resumes=[ResumeResponse.model_validate(r) for r in resumes])


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Get a specific resume by ID."""
    import uuid as uuid_mod
    try:
        rid = uuid_mod.UUID(resume_id)
    except ValueError:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})

    result = await session.execute(
        select(Resume).where(Resume.id == rid, Resume.deleted_at.is_(None))
    )
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})
    if resume.user_id != current_user.id:
        raise HTTPException(403, detail={"code": "forbidden", "message": "Access denied"})

    return ResumeResponse.model_validate(resume)


@router.delete("/{resume_id}", status_code=status.HTTP_200_OK)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Soft-delete a resume."""
    import uuid as uuid_mod
    from datetime import datetime, timezone

    try:
        rid = uuid_mod.UUID(resume_id)
    except ValueError:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})

    result = await session.execute(
        select(Resume).where(Resume.id == rid, Resume.deleted_at.is_(None))
    )
    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})
    if resume.user_id != current_user.id:
        raise HTTPException(403, detail={"code": "forbidden", "message": "Access denied"})

    resume.deleted_at = datetime.now(timezone.utc)
    await session.commit()      # ← added commit for soft delete too
    return {"success": True}

@router.get("/{resume_id}/history", response_model=ResumeHistoryResponse)
async def get_resume_history(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Get the match history for a specific resume."""
    import uuid as uuid_mod
    try:
        rid = uuid_mod.UUID(resume_id)
    except ValueError:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})

    # Verify resume exists and belongs to user
    resume_result = await session.execute(
        select(Resume).where(Resume.id == rid, Resume.deleted_at.is_(None))
    )
    resume = resume_result.scalar_one_or_none()
    if not resume:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})
    if resume.user_id != current_user.id:
        raise HTTPException(403, detail={"code": "forbidden", "message": "Access denied"})

    # Fetch match results with job titles
    result = await session.execute(
        select(MatchResult, JobDescription.title)
        .outerjoin(JobDescription, MatchResult.job_id == JobDescription.id)
        .where(MatchResult.resume_id == rid)
        .where(MatchResult.status == "complete")
        .order_by(MatchResult.created_at.desc())
    )
    
    rows = result.all()
    
    history_items = []
    for match, job_title in rows:
        history_items.append(ResumeHistoryItem(
            match_id=match.id,
            final_score=float(match.final_score) if match.final_score is not None else None,
            status=match.status,
            created_at=match.created_at,
            job_title=job_title
        ))

    return ResumeHistoryResponse(history=history_items)

@router.get("/{resume_id}/versions", response_model=ResumeVersionResponse)
async def get_resume_versions(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Get all versions of a resume."""
    from sqlalchemy import func
    import uuid as uuid_mod
    try:
        rid = uuid_mod.UUID(resume_id)
    except ValueError:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})

    target_result = await session.execute(select(Resume).where(Resume.id == rid, Resume.deleted_at.is_(None)))
    target = target_result.scalar_one_or_none()
    if not target:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})
    if target.user_id != current_user.id:
        raise HTTPException(403, detail={"code": "forbidden", "message": "Access denied"})

    root_id = target.parent_resume_id or target.id

    result = await session.execute(
        select(Resume, func.max(MatchResult.final_score))
        .outerjoin(MatchResult, Resume.id == MatchResult.resume_id)
        .where(
            (Resume.id == root_id) | (Resume.parent_resume_id == root_id),
            Resume.user_id == current_user.id,
            Resume.deleted_at.is_(None)
        )
        .group_by(Resume.id)
        .order_by(Resume.version_number.desc())
    )
    
    rows = result.all()
    versions = []
    for r, best_score in rows:
        versions.append(ResumeVersionItem(
            id=r.id,
            version_number=r.version_number,
            is_active=r.is_active,
            created_at=r.created_at,
            best_score=float(best_score) if best_score is not None else None
        ))
    
    return ResumeVersionResponse(versions=versions)

@router.patch("/{resume_id}/set-active", status_code=status.HTTP_200_OK)
async def set_active_resume_version(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """Set a specific version of a resume as active."""
    import uuid as uuid_mod
    try:
        rid = uuid_mod.UUID(resume_id)
    except ValueError:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})

    target_result = await session.execute(select(Resume).where(Resume.id == rid, Resume.deleted_at.is_(None)))
    target = target_result.scalar_one_or_none()
    if not target:
        raise HTTPException(404, detail={"code": "not_found", "message": "Resume not found"})
    if target.user_id != current_user.id:
        raise HTTPException(403, detail={"code": "forbidden", "message": "Access denied"})

    root_id = target.parent_resume_id or target.id

    family_result = await session.execute(
        select(Resume)
        .where(
            (Resume.id == root_id) | (Resume.parent_resume_id == root_id),
            Resume.user_id == current_user.id,
            Resume.deleted_at.is_(None)
        )
    )
    for r in family_result.scalars().all():
        r.is_active = False

    target.is_active = True
    await session.commit()
    return {"success": True}