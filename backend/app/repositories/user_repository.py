"""
User collection access: CRUD and queries by email/role.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.domain import UserRole


def _oid(s: str) -> ObjectId:
    """Parse Mongo ObjectId from string."""
    return ObjectId(s)


async def insert_user(db: AsyncIOMotorDatabase, doc: Dict[str, Any]) -> str:
    """Insert user document; return id string."""
    doc["created_at"] = datetime.now(timezone.utc)
    doc["is_active"] = doc.get("is_active", True)
    res = await db.users.insert_one(doc)
    return str(res.inserted_id)


async def find_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[Dict[str, Any]]:
    """Lookup user by normalized email."""
    return await db.users.find_one({"email": email.lower().strip()})


async def find_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user by id or None."""
    try:
        return await db.users.find_one({"_id": _oid(user_id)})
    except Exception:
        return None


async def update_user(db: AsyncIOMotorDatabase, user_id: str, patch: Dict[str, Any]) -> bool:
    """Partial update; returns True if matched."""
    try:
        res = await db.users.update_one({"_id": _oid(user_id)}, {"$set": patch})
        return res.matched_count > 0
    except Exception:
        return False


async def list_users(
    db: AsyncIOMotorDatabase,
    *,
    role: Optional[UserRole] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Dict[str, Any]], int]:
    """Paginated user list for admin."""
    filt: Dict[str, Any] = {}
    if role:
        filt["role"] = role.value
    total = await db.users.count_documents(filt)
    cursor = db.users.find(filt).skip(skip).limit(limit).sort("created_at", -1)
    items = await cursor.to_list(length=limit)
    return items, total
