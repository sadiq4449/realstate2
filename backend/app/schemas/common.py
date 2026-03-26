"""Shared schema helpers."""

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Generic API message."""

    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Cursor-style pagination wrapper."""

    items: List[T]
    total: int
    skip: int = 0
    limit: int = 20


class ObjectIdStr(BaseModel):
    """Expose Mongo _id as string in APIs."""

    model_config = {"populate_by_name": True}

    id: str = Field(alias="_id")
