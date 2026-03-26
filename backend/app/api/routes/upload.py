"""
Multipart upload endpoint; stores via storage_service (local/S3).
"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.deps import CurrentUser
from app.services.storage_service import store_file

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_file(user: CurrentUser, file: UploadFile = File(...)):
    """
    Accept image/document for chat or listing; returns public URL.
    """
    if not file.filename:
        raise HTTPException(400, "No filename")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")
    _, url = await store_file(file.filename, content)
    return {"url": url, "filename": file.filename}
