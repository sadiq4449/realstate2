"""Seeker listing alerts (in-app notifications when new listings match criteria)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories import notification_repository


def _city_matches(alert_city: str, prop_city: str) -> bool:
    a = (alert_city or "").strip().lower()
    p = (prop_city or "").strip().lower()
    if not a:
        return True
    return a in p or p in a or a == p


async def create_alert(
    db: AsyncIOMotorDatabase,
    user_id: str,
    *,
    city: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_bedrooms: Optional[int] = None,
) -> str:
    doc: Dict[str, Any] = {
        "user_id": user_id,
        "city": city.strip(),
        "min_price": min_price,
        "max_price": max_price,
        "min_bedrooms": min_bedrooms,
        "active": True,
        "created_at": datetime.now(timezone.utc),
    }
    res = await db.listing_alerts.insert_one(doc)
    return str(res.inserted_id)


async def list_alerts(db: AsyncIOMotorDatabase, user_id: str) -> List[Dict[str, Any]]:
    cursor = db.listing_alerts.find({"user_id": user_id, "active": True}).sort("created_at", -1)
    return await cursor.to_list(length=50)


async def delete_alert(db: AsyncIOMotorDatabase, user_id: str, alert_id: str) -> bool:
    try:
        res = await db.listing_alerts.update_one(
            {"_id": ObjectId(alert_id), "user_id": user_id},
            {"$set": {"active": False}},
        )
        return res.modified_count > 0
    except (InvalidId, Exception):
        return False


async def notify_matching_seekers(db: AsyncIOMotorDatabase, prop: Dict[str, Any]) -> int:
    """When a listing goes live, notify seekers whose alert criteria match."""
    prop_id = str(prop["_id"])
    owner_id = prop.get("owner_id")
    city = prop.get("city") or ""
    rent = float(prop.get("rent_monthly") or 0)
    beds = int(prop.get("bedrooms") or 0)

    cursor = db.listing_alerts.find({"active": True})
    alerts = await cursor.to_list(length=500)
    sent = 0
    for alert in alerts:
        uid = alert.get("user_id")
        if not uid or uid == owner_id:
            continue
        if not _city_matches(alert.get("city") or "", city):
            continue
        mn = alert.get("min_price")
        mx = alert.get("max_price")
        if mn is not None and rent < float(mn):
            continue
        if mx is not None and rent > float(mx):
            continue
        mb = alert.get("min_bedrooms")
        if mb is not None and beds < int(mb):
            continue
        await notification_repository.insert_notification(
            db,
            user_id=uid,
            title="New listing matches your alert",
            body=f"{prop.get('title', 'Listing')} in {city} — PKR {rent:,.0f}/mo",
            data={"property_id": prop_id, "alert_id": str(alert["_id"])},
        )
        sent += 1
    return sent
