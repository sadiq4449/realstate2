"""Seeker listing alerts (in-app notifications for new matches)."""

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException

from app.api.deps import DbDep, SeekerUser
from app.repositories import listing_alert_repository
from app.schemas.user import ListingAlertCreate, ListingAlertOut

router = APIRouter(prefix="/listing-alerts", tags=["listing-alerts"])


def _serialize_alert(doc: dict) -> ListingAlertOut:
    return ListingAlertOut(
        id=str(doc["_id"]),
        city=doc.get("city", ""),
        min_price=doc.get("min_price"),
        max_price=doc.get("max_price"),
        min_bedrooms=doc.get("min_bedrooms"),
        created_at=doc.get("created_at"),
    )


@router.get("", response_model=list)
async def list_my_alerts(db: DbDep, user: SeekerUser):
    rows = await listing_alert_repository.list_alerts(db, str(user["_id"]))
    return [_serialize_alert(r).model_dump(mode="json") for r in rows]


@router.post("", response_model=ListingAlertOut)
async def create_alert_route(db: DbDep, user: SeekerUser, body: ListingAlertCreate):
    aid = await listing_alert_repository.create_alert(
        db,
        str(user["_id"]),
        city=body.city,
        min_price=body.min_price,
        max_price=body.max_price,
        min_bedrooms=body.min_bedrooms,
    )
    try:
        doc = await db.listing_alerts.find_one({"_id": ObjectId(aid), "user_id": str(user["_id"])})
    except InvalidId:
        doc = None
    if not doc:
        raise HTTPException(status_code=500, detail="Failed to load alert")
    return _serialize_alert(doc)


@router.delete("/{alert_id}", response_model=dict)
async def delete_alert_route(db: DbDep, user: SeekerUser, alert_id: str):
    ok = await listing_alert_repository.delete_alert(db, str(user["_id"]), alert_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"ok": True}
