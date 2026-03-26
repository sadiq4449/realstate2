"""Seeker favorites (saved listings)."""

from datetime import datetime, timezone
from typing import List, Tuple

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.models.domain import PropertyStatus


def _oid(s: str) -> ObjectId:
    return ObjectId(s)


async def add_favorite(db: AsyncIOMotorDatabase, user_id: str, property_id: str) -> bool:
    """Return True if inserted; False if duplicate or invalid property."""
    try:
        prop = await db.properties.find_one({"_id": _oid(property_id)})
    except (InvalidId, Exception):
        return False
    if not prop or prop.get("status") != PropertyStatus.APPROVED.value:
        return False
    doc = {
        "user_id": user_id,
        "property_id": property_id,
        "created_at": datetime.now(timezone.utc),
    }
    try:
        await db.favorites.insert_one(doc)
        return True
    except DuplicateKeyError:
        return True
    except Exception:
        return False


async def remove_favorite(db: AsyncIOMotorDatabase, user_id: str, property_id: str) -> bool:
    try:
        res = await db.favorites.delete_one({"user_id": user_id, "property_id": property_id})
        return res.deleted_count > 0
    except Exception:
        return False


async def list_favorite_property_ids(db: AsyncIOMotorDatabase, user_id: str) -> List[str]:
    cursor = db.favorites.find({"user_id": user_id}).sort("created_at", -1)
    rows = await cursor.to_list(length=200)
    return [r["property_id"] for r in rows]


async def is_favorite(db: AsyncIOMotorDatabase, user_id: str, property_id: str) -> bool:
    n = await db.favorites.count_documents({"user_id": user_id, "property_id": property_id})
    return n > 0


async def list_favorite_properties(
    db: AsyncIOMotorDatabase, user_id: str, skip: int = 0, limit: int = 50
) -> Tuple[List[dict], int]:
    """Approved listings the user saved."""
    ids = await list_favorite_property_ids(db, user_id)
    total = len(ids)
    if not ids:
        return [], 0
    slice_ids = ids[skip : skip + limit]
    oids = []
    for s in slice_ids:
        try:
            oids.append(_oid(s))
        except Exception:
            continue
    if not oids:
        return [], total
    cursor = db.properties.find(
        {"_id": {"$in": oids}, "status": PropertyStatus.APPROVED.value}
    )
    rows = await cursor.to_list(length=limit)
    order = {str(i): idx for idx, i in enumerate(oids)}
    rows.sort(key=lambda d: order.get(str(d["_id"]), 999))
    return rows, total
