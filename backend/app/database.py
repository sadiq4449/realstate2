"""
MongoDB async client and database accessor.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    """Lazy-init Motor client."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            get_settings().MONGODB_URI,
            serverSelectionTimeoutMS=8000,
        )
    return _client


def get_database() -> AsyncIOMotorDatabase:
    """Application database handle."""
    return get_client()[get_settings().MONGODB_DB]


async def ensure_indexes() -> None:
    """
    Create indexes for search and common queries.
    Safe to call on startup (idempotent).
    """
    db = get_database()

    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")

    await db.properties.create_index([("status", 1), ("city", 1)])
    await db.properties.create_index([("rent_monthly", 1)])
    await db.properties.create_index([("bedrooms", 1), ("bathrooms", 1)])
    await db.properties.create_index([("title", "text"), ("description", "text"), ("city", "text")])
    await db.properties.create_index([("location", "2dsphere")])
    await db.properties.create_index("owner_id")

    await db.subscription_plans.create_index("active")
    await db.subscriptions.create_index([("user_id", 1), ("status", 1)])
    await db.transactions.create_index("user_id")
    await db.transactions.create_index("subscription_id")
    await db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
    await db.messages.create_index("property_id")
    await db.notifications.create_index([("user_id", 1), ("read", 1)])
    await db.admin_logs.create_index("created_at")
