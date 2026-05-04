"""Resume API routes — upload, list, get, delete."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.dependencies import get_current_user
from app.models.resume import ParseStatus, Resume
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

    resume = Resume(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        filename=file.filename,
        s3_key=s3_key,
        file_size_bytes=len(content),
        mime_type=get_mime_type(ext),
        parse_status=ParseStatus.PENDING,
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