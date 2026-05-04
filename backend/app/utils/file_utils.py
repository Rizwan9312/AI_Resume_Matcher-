"""File utilities — magic byte validation, S3/local storage abstraction."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import BinaryIO

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("file_utils")

# ── Magic Byte Signatures ─────────────────────────────────────────────────

MAGIC_BYTES = {
    ".pdf": b"%PDF",
    ".docx": b"PK\x03\x04",
}

ALLOWED_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024


def validate_magic_bytes(file_content: bytes, extension: str) -> bool:
    """Validate file content against expected magic bytes for the extension."""
    expected = MAGIC_BYTES.get(extension.lower())
    if expected is None:
        return False
    return file_content[:len(expected)] == expected


def validate_file_extension(filename: str) -> str | None:
    """Return the lowercase extension if allowed, or None."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in ALLOWED_MIME_TYPES:
        return ext
    return None


def get_mime_type(extension: str) -> str:
    """Get MIME type for a file extension."""
    return ALLOWED_MIME_TYPES.get(extension.lower(), "application/octet-stream")


# ── Storage Abstraction ───────────────────────────────────────────────────

def generate_s3_key(user_id: str, filename: str) -> str:
    """Generate a unique S3-compatible key for a file."""
    unique_id = uuid.uuid4().hex[:12]
    ext = os.path.splitext(filename)[1].lower()
    return f"resumes/{user_id}/{unique_id}{ext}"


async def upload_file_local(file_content: bytes, s3_key: str) -> str:
    """Store file on local disk (dev mode). Returns the local path."""
    upload_dir = Path(settings.LOCAL_UPLOAD_DIR)
    file_path = upload_dir / s3_key
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(file_content)
    logger.info("file.uploaded_local", path=str(file_path), size=len(file_content))
    return str(file_path)


async def upload_file_s3(file_content: bytes, s3_key: str) -> str:
    """Upload file to S3. Returns the S3 key."""
    try:
        import boto3

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
        )
        logger.info("file.uploaded_s3", key=s3_key, size=len(file_content))
        return s3_key
    except Exception as exc:
        logger.error("file.upload_s3_failed", key=s3_key, error=str(exc))
        raise


async def upload_file(file_content: bytes, s3_key: str) -> str:
    """Upload file using the configured storage backend."""
    if settings.STORAGE_BACKEND == "s3":
        return await upload_file_s3(file_content, s3_key)
    return await upload_file_local(file_content, s3_key)


async def download_file_local(s3_key: str) -> bytes | None:
    """Download a file from local storage."""
    file_path = Path(settings.LOCAL_UPLOAD_DIR) / s3_key
    if file_path.exists():
        return file_path.read_bytes()
    return None


async def download_file(s3_key: str) -> bytes | None:
    """Download file using the configured storage backend."""
    if settings.STORAGE_BACKEND == "s3":
        try:
            import boto3

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            response = s3_client.get_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
            )
            return response["Body"].read()
        except Exception as exc:
            logger.error("file.download_s3_failed", key=s3_key, error=str(exc))
            return None
    return await download_file_local(s3_key)
