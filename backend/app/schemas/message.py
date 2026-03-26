"""Chat messages and conversations."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Send text or attachment reference."""

    property_id: str
    recipient_id: str
    body: str = Field(default="", max_length=8000)
    attachment_url: Optional[str] = None


class MessageOut(BaseModel):
    """Stored message."""

    id: str
    conversation_id: str
    property_id: str
    sender_id: str
    recipient_id: str
    body: str
    attachment_url: Optional[str] = None
    created_at: datetime


class ConversationOut(BaseModel):
    """Inbox thread summary."""

    conversation_id: str
    property_id: str
    other_user_id: str
    other_user_name: str
    last_message: str
    last_at: datetime
    unread_count: int = 0
