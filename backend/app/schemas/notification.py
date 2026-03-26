"""In-app notifications."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class NotificationOut(BaseModel):
    """User notification."""

    id: str
    user_id: str
    title: str
    body: str
    read: bool
    data: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
