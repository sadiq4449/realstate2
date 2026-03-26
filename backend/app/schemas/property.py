"""Property listing schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.domain import PropertyStatus


class GeoPoint(BaseModel):
    """GeoJSON Point for map search."""

    type: str = "Point"
    coordinates: List[float]  # [lng, lat]


class PropertyCreate(BaseModel):
    """Owner creates listing."""

    title: str
    description: str
    city: str
    address: str
    rent_monthly: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    bathrooms: int = Field(ge=0)
    furnished: bool = False
    amenities: List[str] = []
    images: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PropertyUpdate(BaseModel):
    """Partial update."""

    title: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    rent_monthly: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    furnished: Optional[bool] = None
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PropertyOut(BaseModel):
    """API property document."""

    id: str
    owner_id: str
    title: str
    description: str
    city: str
    address: str
    rent_monthly: float
    bedrooms: int
    bathrooms: int
    furnished: bool
    amenities: List[str]
    images: List[str]
    status: PropertyStatus
    location: Optional[GeoPoint] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PropertySearchParams(BaseModel):
    """Query filters for search endpoint."""

    q: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[int] = None
    furnished: Optional[bool] = None
    amenities: Optional[str] = None  # comma-separated
    city: Optional[str] = None
    skip: int = 0
    limit: int = 20


class PropertyModeration(BaseModel):
    """Admin approve/reject."""

    status: PropertyStatus
    reason: Optional[str] = None
