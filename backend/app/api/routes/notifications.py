"""User notification feed."""

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DbDep
from app.api.serializers import serialize_notification
from app.repositories import notification_repository

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list)
async def list_notifications(db: DbDep, user: CurrentUser):
    """Recent notifications for navbar."""
    rows = await notification_repository.list_for_user(db, str(user["_id"]))
    return [serialize_notification(r).model_dump(mode="json") for r in rows]


@router.post("/{notif_id}/read")
async def mark_notification_read(notif_id: str, db: DbDep, user: CurrentUser):
    """Mark single notification read."""
    ok = await notification_repository.mark_read(db, notif_id, str(user["_id"]))
    if not ok:
        raise HTTPException(404, "Not found")
    return {"ok": True}
