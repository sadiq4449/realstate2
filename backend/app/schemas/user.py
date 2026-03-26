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
