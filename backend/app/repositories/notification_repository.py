"""Notifications and admin audit logs."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


def _oid(s: str) -> ObjectId:
    return ObjectId(s)


async def insert_notification(
    db: AsyncIOMotorDatabase,
    *,
    user_id: str,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
) -> str:
    doc = {
        "user_id": user_id,
        "title": title,
        "body": body,
        "read": False,
        "data": data or {},
        "created_at": datetime.now(timezone.utc),
    }
    res = await db.notifications.insert_one(doc)
    return str(res.inserted_id)


async def list_for_user(db: AsyncIOMotorDatabase, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {"user_id": user_id}
    if unread_only:
        filt["read"] = False
    cursor = db.notifications.find(filt).sort("created_at", -1).limit(100)
    return await cursor.to_list(length=100)


async def mark_read(db: AsyncIOMotorDatabase, notif_id: str, user_id: str) -> bool:
    try:
        res = await db.notifications.update_one(
            {"_id": _oid(notif_id), "user_id": user_id}, {"$set": {"read": True}}
        )
        return res.modified_count > 0
    except Exception:
        return False


async def insert_admin_log(
    db: AsyncIOMotorDatabase,
    *,
    admin_id: str,
    action: str,
    target_type: str,
    target_id: str,
    detail: Optional[Dict[str, Any]] = None,
) -> None:
    await db.admin_logs.insert_one(
        {
            "admin_id": admin_id,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "detail": detail or {},
            "created_at": datetime.now(timezone.utc),
        }
    )
