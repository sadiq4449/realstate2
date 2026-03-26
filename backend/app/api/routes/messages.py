"""
REST chat: conversations, history; WebSocket handled in main.
"""

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DbDep
from app.api.serializers import serialize_message
from app.repositories import message_repository, property_repository, user_repository
from app.schemas.message import MessageCreate, MessageOut
from app.ws.manager import manager as ws_manager

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=MessageOut)
async def send_message(payload: MessageCreate, db: DbDep, user: CurrentUser):
    """
    Persist message and push to WebSocket subscribers.
    Validates property exists and recipient is owner or seeker context.
    """
    prop = await property_repository.find_by_id(db, payload.property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    sender_id = str(user["_id"])
    recipient_id = payload.recipient_id
    if recipient_id == sender_id:
        raise HTTPException(400, "Cannot message yourself")

    owner_id = prop["owner_id"]
    if owner_id not in (sender_id, recipient_id):
        raise HTTPException(403, "Owner must be a participant")
    if sender_id == owner_id and recipient_id == owner_id:
        raise HTTPException(400, "Invalid recipient")

    conv = message_repository.make_conversation_id(payload.property_id, sender_id, recipient_id)
    mid = await message_repository.insert_message(
        db,
        conversation_id=conv,
        property_id=payload.property_id,
        sender_id=sender_id,
        recipient_id=recipient_id,
        body=payload.body,
        attachment_url=payload.attachment_url,
    )
    doc = await db.messages.find_one({"_id": ObjectId(mid)})
    out = serialize_message(doc)
    event = {"type": "message", "payload": out.model_dump(mode="json")}
    await ws_manager.broadcast_conversation(conv, event)
    await ws_manager.broadcast_admins({**event, "conversation_id": conv, "monitor": True})
    return out


@router.get("/conversations", response_model=list)
async def list_conversations(db: DbDep, user: CurrentUser):
    """Inbox summaries for current user."""
    uid = str(user["_id"])
    groups = await message_repository.conversations_for_user(db, uid)
    result = []
    for g in groups:
        d = g["last_doc"]
        other = d["recipient_id"] if d["sender_id"] == uid else d["sender_id"]
        other_user = await user_repository.find_by_id(db, other)
        name = other_user["full_name"] if other_user else other
        result.append(
            {
                "conversation_id": d["conversation_id"],
                "property_id": d["property_id"],
                "other_user_id": other,
                "other_user_name": name,
                "last_message": d.get("body", "")[:200],
                "last_at": d["created_at"],
            }
        )
    result.sort(key=lambda x: x["last_at"], reverse=True)
    return result


@router.get("/{conversation_id}", response_model=list)
async def conversation_messages(conversation_id: str, db: DbDep, user: CurrentUser):
    """Message history if participant or admin."""
    uid = str(user["_id"])
    role = user.get("role")
    if role != "admin":
        # verify participation: any message in conv has user as sender/recipient
        one = await db.messages.find_one(
            {
                "conversation_id": conversation_id,
                "$or": [{"sender_id": uid}, {"recipient_id": uid}],
            }
        )
        if not one:
            raise HTTPException(403, "Not part of conversation")
    rows = await message_repository.list_messages(db, conversation_id)
    return [serialize_message(r).model_dump(mode="json") for r in rows]
