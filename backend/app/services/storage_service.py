"""
File upload abstraction: local disk (dev) or S3 (prod).
Cloudinary can be added similarly using httpx + signed upload.
"""

import uuid
from pathlib import Path
from typing import Tuple

import aiofiles
import boto3

from app.config import get_settings


async def save_upload_local(filename: str, content: bytes) -> Tuple[str, str]:
    """
    Write bytes to LOCAL_UPLOAD_DIR; return (relative_path, public_url).
    """
    settings = get_settings()
    base = Path(settings.LOCAL_UPLOAD_DIR)
    base.mkdir(parents=True, exist_ok=True)
    ext = Path(filename).suffix or ".bin"
    safe = f"{uuid.uuid4().hex}{ext}"
    dest = base / safe
    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)
    rel = f"uploads/{safe}"
    url = f"{settings.PUBLIC_MEDIA_BASE_URL.rstrip('/')}/{safe}"
    return rel, url


def save_upload_s3(filename: str, content: bytes) -> Tuple[str, str]:
    """Upload to S3; return key and HTTPS URL."""
    settings = get_settings()
    if not settings.AWS_S3_BUCKET:
        raise RuntimeError("S3 bucket not configured")
    ext = Path(filename).suffix or ".bin"
    key = f"media/{uuid.uuid4().hex}{ext}"
    client = boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    client.put_object(Bucket=settings.AWS_S3_BUCKET, Key=key, Body=content)
    url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
    return key, url


async def store_file(filename: str, content: bytes) -> Tuple[str, str]:
    """
    Route to configured STORAGE_MODE.
    Returns (storage_key, public_url).
    """
    settings = get_settings()
    mode = (settings.STORAGE_MODE or "local").lower()
    if mode == "s3":
        return save_upload_s3(filename, content)
    return await save_upload_local(filename, content)
