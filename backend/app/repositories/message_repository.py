"""
Messages and conversation_id derivation for owner/seeker threads.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


def _oid(s: str) -> ObjectId:
    return ObjectId(s)


def make_conversation_id(property_id: str, user_a: str, user_b: str) -> str:
    """Deterministic room id from two participants."""
    a, b = sorted([user_a, user_b])
    return f"{property_id}:{a}:{b}"


async def insert_message(
    db: AsyncIOMotorDatabase,
    *,
    conversation_id: str,
    property_id: str,
    sender_id: str,
    recipient_id: str,
    body: str,
    attachment_url: Optional[str] = None,
) -> str:
    now = datetime.now(timezone.utc)
    doc = {
        "conversation_id": conversation_id,
        "property_id": property_id,
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "body": body or "",
        "attachment_url": attachment_url,
        "created_at": now,
    }
    res = await db.messages.insert_one(doc)
    return str(res.inserted_id)


async def list_messages(
    db: AsyncIOMotorDatabase, conversation_id: str, skip: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    cursor = (
        db.messages.find({"conversation_id": conversation_id})
        .sort("created_at", 1)
        .skip(skip)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def conversations_for_user(db: AsyncIOMotorDatabase, user_id: str) -> List[Dict[str, Any]]:
    """
    Aggregate last message per conversation involving user.
    """
    pipeline: List[Dict[str, Any]] = [
        {"$match": {"$or": [{"sender_id": user_id}, {"recipient_id": user_id}]}},
        {"$sort": {"created_at": -1}},
        {
            "$group": {
                "_id": "$conversation_id",
                "last_doc": {"$first": "$$ROOT"},
            }
        },
    ]
    return await db.messages.aggregate(pipeline).to_list(length=200)
