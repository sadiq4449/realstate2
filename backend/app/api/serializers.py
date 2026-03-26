"""Map Mongo documents to Pydantic response models."""

from typing import Any, Dict

from app.models.domain import PropertyStatus, SubscriptionStatus, TransactionStatus, UserRole
from app.schemas.message import MessageOut
from app.schemas.notification import NotificationOut
from app.schemas.property import GeoPoint, PropertyOut
from app.schemas.subscription import PlanOut, SubscriptionOut, TransactionOut
from app.schemas.user import UserOut


def serialize_user(doc: Dict[str, Any]) -> UserOut:
    """Normalize user bson to API shape."""
    return UserOut(
        id=str(doc["_id"]),
        email=doc["email"],
        full_name=doc["full_name"],
        role=UserRole(doc["role"]),
        phone=doc.get("phone"),
        is_active=doc.get("is_active", True),
        created_at=doc.get("created_at"),
    )


def serialize_property(doc: Dict[str, Any]) -> PropertyOut:
    """Property document to response."""
    loc = doc.get("location")
    geo = None
    if loc and loc.get("type") == "Point" and loc.get("coordinates"):
        geo = GeoPoint(coordinates=loc["coordinates"])
    return PropertyOut(
        id=str(doc["_id"]),
        owner_id=doc["owner_id"],
        title=doc["title"],
        description=doc["description"],
        city=doc["city"],
        address=doc["address"],
        rent_monthly=float(doc["rent_monthly"]),
        bedrooms=int(doc["bedrooms"]),
        bathrooms=int(doc["bathrooms"]),
        furnished=bool(doc.get("furnished", False)),
        amenities=list(doc.get("amenities") or []),
        images=list(doc.get("images") or []),
        videos=list(doc.get("videos") or []),
        view_count=int(doc.get("view_count") or 0),
        status=PropertyStatus(doc["status"]),
        location=geo,
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
    )


def serialize_plan(doc: Dict[str, Any]) -> PlanOut:
    return PlanOut(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description", ""),
        price_monthly=float(doc["price_monthly"]),
        currency=doc.get("currency", "usd"),
        max_listings=int(doc.get("max_listings", 5)),
        search_boost=int(doc.get("search_boost", 0)),
        features=dict(doc.get("features") or {}),
        active=bool(doc.get("active", True)),
    )


def serialize_subscription(doc: Dict[str, Any]) -> SubscriptionOut:
    return SubscriptionOut(
        id=str(doc["_id"]),
        user_id=doc["user_id"],
        plan_id=str(doc["plan_id"]) if doc.get("plan_id") is not None else "",
        status=SubscriptionStatus(doc["status"]),
        current_period_end=doc.get("current_period_end"),
        auto_renew=bool(doc.get("auto_renew", True)),
        stripe_subscription_id=doc.get("stripe_subscription_id"),
    )


def serialize_transaction(doc: Dict[str, Any]) -> TransactionOut:
    return TransactionOut(
        id=str(doc["_id"]),
        user_id=doc["user_id"],
        subscription_id=str(doc["subscription_id"]) if doc.get("subscription_id") else None,
        amount=float(doc["amount"]),
        currency=doc.get("currency", "usd"),
        status=TransactionStatus(doc["status"]),
        provider=doc.get("provider", "mock"),
        invoice_number=doc.get("invoice_number"),
        metadata=dict(doc.get("metadata") or {}),
        created_at=doc.get("created_at"),
    )


def serialize_message(doc: Dict[str, Any]) -> MessageOut:
    return MessageOut(
        id=str(doc["_id"]),
        conversation_id=doc["conversation_id"],
        property_id=doc["property_id"],
        sender_id=doc["sender_id"],
        recipient_id=doc["recipient_id"],
        body=doc.get("body", ""),
        attachment_url=doc.get("attachment_url"),
        created_at=doc["created_at"],
    )


def serialize_notification(doc: Dict[str, Any]) -> NotificationOut:
    return NotificationOut(
        id=str(doc["_id"]),
        user_id=doc["user_id"],
        title=doc["title"],
        body=doc["body"],
        read=bool(doc.get("read", False)),
        data=dict(doc.get("data") or {}),
        created_at=doc.get("created_at"),
    )
