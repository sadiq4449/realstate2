"""Admin operation payloads."""

from typing import Optional

from pydantic import BaseModel

from app.models.domain import PropertyStatus


class PropertyModerateBody(BaseModel):
    """Approve/reject listing."""

    status: PropertyStatus
    reason: Optional[str] = None
