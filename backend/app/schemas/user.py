"""User-related schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.domain import UserRole


class UserCreate(BaseModel):
    """Registration payload."""

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    role: UserRole = UserRole.SEEKER
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """Login credentials."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Public user profile."""

    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    """Profile update (non-role for self-service)."""

    full_name: Optional[str] = None
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    """JWT pair (refresh optional for MVP)."""

    access_token: str
    token_type: str = "bearer"


class AdminUserUpdate(BaseModel):
    """Admin can toggle active flag."""

    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class ListingAlertCreate(BaseModel):
    """Seeker alert when new approved listings match filters."""

    city: str = Field(min_length=1, max_length=120)
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = Field(default=None, ge=0)


class ListingAlertOut(BaseModel):
    """Saved alert row."""

    id: str
    city: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    created_at: Optional[datetime] = None


class FavoriteBody(BaseModel):
    """Add saved listing."""

    property_id: str = Field(min_length=1)
