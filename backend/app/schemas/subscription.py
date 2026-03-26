"""Subscription plans, user subscriptions, mock/Stripe payments."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.models.domain import SubscriptionStatus, TransactionStatus


class PlanCreate(BaseModel):
    """Admin-defined plan."""

    name: str
    description: str = ""
    price_monthly: float = Field(gt=0)
    currency: str = "usd"
    max_listings: int = Field(ge=1, default=5)
    features: Dict[str, Any] = {}


class PlanUpdate(BaseModel):
    """Update plan pricing/metadata."""

    name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = None
    currency: Optional[str] = None
    max_listings: Optional[int] = None
    features: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class PlanOut(BaseModel):
    """Plan returned to clients."""

    id: str
    name: str
    description: str
    price_monthly: float
    currency: str
    max_listings: int
    features: Dict[str, Any]
    active: bool = True


class SubscribeRequest(BaseModel):
    """Start subscription — mock or Stripe customer flow."""

    plan_id: str
    use_mock_payment: bool = True
    payment_method_id: Optional[str] = None  # Stripe PM id when not mock


class SubscriptionOut(BaseModel):
    """User's active subscription row."""

    id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_end: Optional[datetime] = None
    auto_renew: bool = True
    stripe_subscription_id: Optional[str] = None


class TransactionOut(BaseModel):
    """Invoice/payment record."""

    id: str
    user_id: str
    subscription_id: Optional[str] = None
    amount: float
    currency: str
    status: TransactionStatus
    provider: str = "mock"
    invoice_number: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
