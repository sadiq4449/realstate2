"""
Property CRUD for owners; public detail for approved listings.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import CurrentUser, DbDep, OwnerUser, get_current_user_optional
from app.api.serializers import serialize_property
from app.models.domain import PropertyStatus, UserRole
from app.repositories import notification_repository, property_repository, subscription_repository
from app.schemas.property import PropertyCreate, PropertyOut, PropertyUpdate

router = APIRouter(prefix="/properties", tags=["properties"])


async def _owner_listing_capacity(db, owner_id: str) -> tuple[int, int]:
    """Return (current_count, max_allowed). Default max 3 without subscription."""
    sub = await subscription_repository.get_active_subscription(db, owner_id)
    max_allowed = 3
    if sub:
        plan = await subscription_repository.get_plan(db, str(sub.get("plan_id", "")))
        if plan:
            max_allowed = int(plan.get("max_listings", 5))
    filt = {
        "owner_id": owner_id,
        "status": {"$in": [PropertyStatus.PENDING.value, PropertyStatus.APPROVED.value, PropertyStatus.DRAFT.value]},
    }
    count = await db.properties.count_documents(filt)
    return count, max_allowed


@router.post("", response_model=PropertyOut)
async def create_property(payload: PropertyCreate, db: DbDep, user: OwnerUser):
    """Owner submits listing (pending approval)."""
    count, max_allowed = await _owner_listing_capacity(db, str(user["_id"]))
    if count >= max_allowed:
        raise HTTPException(
            status_code=403,
            detail=f"Listing limit reached ({max_allowed}). Upgrade subscription.",
        )
    data = payload.model_dump()
    pid = await property_repository.insert_property(db, str(user["_id"]), data)
    doc = await property_repository.find_by_id(db, pid)
    await notification_repository.insert_notification(
        db,
        user_id=str(user["_id"]),
        title="Listing submitted",
        body="Your property is pending admin approval.",
        data={"property_id": pid},
    )
    return serialize_property(doc)


@router.get("/mine", response_model=dict)
async def my_properties(
    db: DbDep,
    user: CurrentUser,
    skip: int = 0,
    limit: int = 50,
):
    """Owner dashboard list; requires owner role for full UX but returns empty for others."""
    if user.get("role") != UserRole.OWNER.value:
        return {"items": [], "total": 0, "skip": skip, "limit": limit}
    items, total = await property_repository.list_by_owner(db, str(user["_id"]), skip=skip, limit=limit)
    return {
        "items": [serialize_property(x).model_dump() for x in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.patch("/{property_id}", response_model=PropertyOut)
async def update_property_route(
    property_id: str,
    payload: PropertyUpdate,
    db: DbDep,
    user: OwnerUser,
):
    """Owner edits own listing."""
    patch = payload.model_dump(exclude_unset=True)
    ok = await property_repository.update_property(db, property_id, str(user["_id"]), patch)
    if not ok:
        raise HTTPException(404, "Property not found")
    doc = await property_repository.find_by_id(db, property_id)
    return serialize_property(doc)


@router.delete("/{property_id}")
async def delete_property_route(property_id: str, db: DbDep, user: OwnerUser):
    """Owner removes listing."""
    ok = await property_repository.delete_property(db, property_id, str(user["_id"]))
    if not ok:
        raise HTTPException(404, "Property not found")
    return {"ok": True}


@router.get("/{property_id}", response_model=PropertyOut)
async def get_property(
    property_id: str,
    db: DbDep,
    user: Optional[dict] = Depends(get_current_user_optional),
):
    """Public detail: approved for everyone; owner/admin see non-approved."""
    doc = await property_repository.find_by_id(db, property_id)
    if not doc:
        raise HTTPException(404, "Not found")
    if doc.get("status") != PropertyStatus.APPROVED.value:
        if not user:
            raise HTTPException(404, "Not found")
        uid = str(user["_id"])
        if doc["owner_id"] != uid and user.get("role") != UserRole.ADMIN.value:
            raise HTTPException(404, "Not found")
    return serialize_property(doc)
