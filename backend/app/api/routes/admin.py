"""
Super admin: listing moderation, pending queue, audit trail hooks.
"""

from fastapi import APIRouter, HTTPException

from app.api.deps import AdminUser, DbDep
from app.api.serializers import serialize_property
from app.models.domain import PropertyStatus
from app.repositories import notification_repository, property_repository, user_repository
from app.schemas.admin_ops import PropertyModerateBody

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/properties/pending", response_model=dict)
async def pending_listings(db: DbDep, admin: AdminUser, skip: int = 0, limit: int = 50):
    """Approval queue."""
    items, total = await property_repository.list_pending(db, skip=skip, limit=limit)
    return {
        "items": [serialize_property(x).model_dump() for x in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/properties/{property_id}/moderate")
async def moderate_property(
    property_id: str,
    body: PropertyModerateBody,
    db: DbDep,
    admin: AdminUser,
):
    """Approve or reject listing."""
    status = body.status
    reason = body.reason
    if status not in (PropertyStatus.APPROVED, PropertyStatus.REJECTED):
        raise HTTPException(400, "Only approved/rejected allowed here")
    doc = await property_repository.find_by_id(db, property_id)
    if not doc:
        raise HTTPException(404, "Not found")
    await property_repository.set_status(db, property_id, status, reason=reason)
    owner_id = doc["owner_id"]
    await notification_repository.insert_notification(
        db,
        user_id=owner_id,
        title="Listing " + status.value,
        body=reason or f"Your listing was {status.value}.",
        data={"property_id": property_id},
    )
    await notification_repository.insert_admin_log(
        db,
        admin_id=str(admin["_id"]),
        action="property_moderate",
        target_type="property",
        target_id=property_id,
        detail={"status": status.value, "reason": reason},
    )
    fresh = await property_repository.find_by_id(db, property_id)
    return serialize_property(fresh)
