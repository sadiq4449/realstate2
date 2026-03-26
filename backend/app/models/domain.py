"""Enumerations for roles, listing status, and subscription state."""

from enum import Enum


class UserRole(str, Enum):
    """Application roles."""

    OWNER = "owner"
    SEEKER = "seeker"
    ADMIN = "admin"


class PropertyStatus(str, Enum):
    """Listing moderation lifecycle."""

    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SubscriptionStatus(str, Enum):
    """Billing state for owner plans."""

    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"


class TransactionStatus(str, Enum):
    """Payment record state."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
