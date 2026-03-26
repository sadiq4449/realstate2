"""
Property listings: CRUD, search filters, geo queries.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.domain import PropertyStatus


def _oid(s: str) -> ObjectId:
    return ObjectId(s)


def _location(lat: Optional[float], lng: Optional[float]) -> Optional[Dict[str, Any]]:
    """Build GeoJSON Point if coords present."""
    if lat is None or lng is None:
        return None
    return {"type": "Point", "coordinates": [lng, lat]}


async def insert_property(db: AsyncIOMotorDatabase, owner_id: str, data: Dict[str, Any]) -> str:
    """Create listing; default pending for moderation."""
    now = datetime.now(timezone.utc)
    doc = {
        "owner_id": owner_id,
        "title": data["title"],
        "description": data["description"],
        "city": data["city"],
        "address": data["address"],
        "rent_monthly": float(data["rent_monthly"]),
        "bedrooms": int(data["bedrooms"]),
        "bathrooms": int(data["bathrooms"]),
        "furnished": bool(data.get("furnished", False)),
        "amenities": list(data.get("amenities") or []),
        "images": list(data.get("images") or []),
        "status": PropertyStatus.PENDING.value,
        "location": _location(data.get("latitude"), data.get("longitude")),
        "created_at": now,
        "updated_at": now,
    }
    res = await db.properties.insert_one(doc)
    return str(res.inserted_id)


async def update_property(
    db: AsyncIOMotorDatabase, prop_id: str, owner_id: Optional[str], patch: Dict[str, Any]
) -> bool:
    """Update if exists; optional owner guard."""
    try:
        filt: Dict[str, Any] = {"_id": _oid(prop_id)}
        if owner_id:
            filt["owner_id"] = owner_id
        patch = {k: v for k, v in patch.items() if v is not None}
        if "latitude" in patch or "longitude" in patch:
            # merge lat/lng from patch + existing if partial
            cur = await db.properties.find_one({"_id": _oid(prop_id)})
            lat = patch.pop("latitude", None)
            lng = patch.pop("longitude", None)
            if cur:
                loc = cur.get("location") or {}
                coords = loc.get("coordinates") or [None, None]
                new_lng = lng if lng is not None else (coords[0] if len(coords) > 0 else None)
                new_lat = lat if lat is not None else (coords[1] if len(coords) > 1 else None)
                patch["location"] = _location(new_lat, new_lng)
        patch["updated_at"] = datetime.now(timezone.utc)
        res = await db.properties.update_one(filt, {"$set": patch})
        return res.matched_count > 0
    except Exception:
        return False


async def find_by_id(db: AsyncIOMotorDatabase, prop_id: str) -> Optional[Dict[str, Any]]:
    try:
        return await db.properties.find_one({"_id": _oid(prop_id)})
    except Exception:
        return None


async def delete_property(db: AsyncIOMotorDatabase, prop_id: str, owner_id: str) -> bool:
    try:
        res = await db.properties.delete_one({"_id": _oid(prop_id), "owner_id": owner_id})
        return res.deleted_count > 0
    except Exception:
        return False


async def set_status(
    db: AsyncIOMotorDatabase, prop_id: str, status: PropertyStatus, reason: Optional[str] = None
) -> bool:
    """Admin moderation."""
    try:
        patch: Dict[str, Any] = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc),
        }
        if reason is not None:
            patch["moderation_reason"] = reason
        res = await db.properties.update_one({"_id": _oid(prop_id)}, {"$set": patch})
        return res.matched_count > 0
    except Exception:
        return False


async def list_by_owner(
    db: AsyncIOMotorDatabase, owner_id: str, skip: int = 0, limit: int = 50
) -> Tuple[List[Dict[str, Any]], int]:
    filt = {"owner_id": owner_id}
    total = await db.properties.count_documents(filt)
    cursor = db.properties.find(filt).skip(skip).limit(limit).sort("updated_at", -1)
    items = await cursor.to_list(length=limit)
    return items, total


async def search_properties(
    db: AsyncIOMotorDatabase,
    *,
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_bedrooms: Optional[int] = None,
    max_bedrooms: Optional[int] = None,
    min_bathrooms: Optional[int] = None,
    furnished: Optional[bool] = None,
    amenities: Optional[List[str]] = None,
    city: Optional[str] = None,
    status: PropertyStatus = PropertyStatus.APPROVED,
    near_lng: Optional[float] = None,
    near_lat: Optional[float] = None,
    max_distance_m: Optional[float] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Text + filter search. Optional $near sphere for map radius (meters).
    """
    filt: Dict[str, Any] = {"status": status.value}

    if city:
        filt["city"] = {"$regex": city, "$options": "i"}
    if min_price is not None or max_price is not None:
        filt["rent_monthly"] = {}
        if min_price is not None:
            filt["rent_monthly"]["$gte"] = min_price
        if max_price is not None:
            filt["rent_monthly"]["$lte"] = max_price
    if min_bedrooms is not None:
        filt.setdefault("bedrooms", {})["$gte"] = min_bedrooms
    if max_bedrooms is not None:
        filt.setdefault("bedrooms", {})["$lte"] = max_bedrooms
    if min_bathrooms is not None:
        filt.setdefault("bathrooms", {})["$gte"] = min_bathrooms
    if furnished is not None:
        filt["furnished"] = furnished
    if amenities:
        filt["amenities"] = {"$all": amenities}

    if near_lng is not None and near_lat is not None and max_distance_m:
        filt["location"] = {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [near_lng, near_lat]},
                "$maxDistance": max_distance_m,
            }
        }

    if q and str(q).strip():
        filt["$text"] = {"$search": q.strip()}

    total = await db.properties.count_documents(filt)
    cursor = db.properties.find(filt).skip(skip).limit(limit).sort("rent_monthly", 1)
    items = await cursor.to_list(length=limit)
    return items, total


async def list_pending(db: AsyncIOMotorDatabase, skip: int = 0, limit: int = 50) -> Tuple[List[Dict[str, Any]], int]:
    filt = {"status": PropertyStatus.PENDING.value}
    total = await db.properties.count_documents(filt)
    cursor = db.properties.find(filt).skip(skip).limit(limit).sort("created_at", 1)
    items = await cursor.to_list(length=limit)
    return items, total
