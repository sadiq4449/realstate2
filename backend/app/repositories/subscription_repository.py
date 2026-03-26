"""
Subscription plans, user subscriptions, transactions (invoices).
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
import uuid

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.domain import SubscriptionStatus, TransactionStatus


def _oid(s: str) -> ObjectId:
    return ObjectId(s)


async def insert_plan(db: AsyncIOMotorDatabase, doc: Dict[str, Any]) -> str:
    doc.setdefault("active", True)
    doc["created_at"] = datetime.now(timezone.utc)
    res = await db.subscription_plans.insert_one(doc)
    return str(res.inserted_id)


async def list_plans(db: AsyncIOMotorDatabase, active_only: bool = True) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if active_only:
        filt["active"] = True
    cursor = db.subscription_plans.find(filt).sort("price_monthly", 1)
    return await cursor.to_list(length=100)


async def get_plan(db: AsyncIOMotorDatabase, plan_id: str) -> Optional[Dict[str, Any]]:
    try:
        return await db.subscription_plans.find_one({"_id": _oid(plan_id)})
    except Exception:
        return None


async def update_plan(db: AsyncIOMotorDatabase, plan_id: str, patch: Dict[str, Any]) -> bool:
    try:
        patch = {k: v for k, v in patch.items() if v is not None}
        res = await db.subscription_plans.update_one({"_id": _oid(plan_id)}, {"$set": patch})
        return res.matched_count > 0
    except Exception:
        return False


async def upsert_user_subscription(
    db: AsyncIOMotorDatabase,
    user_id: str,
    plan_id: str,
    *,
    stripe_sub_id: Optional[str] = None,
    period_days: int = 30,
) -> str:
    """Create or replace active subscription for user (single plan MVP)."""
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=period_days)
    existing = await db.subscriptions.find_one({"user_id": user_id, "status": SubscriptionStatus.ACTIVE.value})
    doc = {
        "user_id": user_id,
        "plan_id": str(plan_id),
        "status": SubscriptionStatus.ACTIVE.value,
        "current_period_start": now,
        "current_period_end": end,
        "auto_renew": True,
        "stripe_subscription_id": stripe_sub_id,
        "updated_at": now,
    }
    if existing:
        await db.subscriptions.update_one({"_id": existing["_id"]}, {"$set": doc})
        return str(existing["_id"])
    doc["created_at"] = now
    res = await db.subscriptions.insert_one(doc)
    return str(res.inserted_id)


async def get_active_subscription(db: AsyncIOMotorDatabase, user_id: str) -> Optional[Dict[str, Any]]:
    return await db.subscriptions.find_one(
        {"user_id": user_id, "status": SubscriptionStatus.ACTIVE.value}
    )


async def insert_transaction(
    db: AsyncIOMotorDatabase,
    *,
    user_id: str,
    subscription_id: Optional[str],
    amount: float,
    currency: str,
    status: TransactionStatus,
    provider: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    inv = f"INV-{uuid.uuid4().hex[:12].upper()}"
    doc = {
        "user_id": user_id,
        "subscription_id": subscription_id,
        "amount": amount,
        "currency": currency,
        "status": status.value,
        "provider": provider,
        "invoice_number": inv,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc),
    }
    res = await db.transactions.insert_one(doc)
    return str(res.inserted_id)


async def list_transactions_for_user(
    db: AsyncIOMotorDatabase, user_id: str, skip: int = 0, limit: int = 50
) -> Tuple[List[Dict[str, Any]], int]:
    filt = {"user_id": user_id}
    total = await db.transactions.count_documents(filt)
    cursor = db.transactions.find(filt).sort("created_at", -1).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)
    return items, total


async def run_auto_renewal_tick(db: AsyncIOMotorDatabase) -> int:
    """
    Mark past-due and extend period for auto_renew mock (no real charge).
    Returns number of renewed rows.
    """
    now = datetime.now(timezone.utc)
    renewed = 0
    cursor = db.subscriptions.find(
        {"status": SubscriptionStatus.ACTIVE.value, "auto_renew": True, "current_period_end": {"$lt": now}}
    )
    async for sub in cursor:
        pid = sub.get("plan_id")
        plan = await get_plan(db, str(pid)) if pid is not None else None
        if not plan and pid is not None:
            try:
                plan = await db.subscription_plans.find_one({"_id": ObjectId(str(pid))})
            except Exception:
                plan = None
        price = float(plan["price_monthly"]) if plan else 0.0
        currency = plan.get("currency", "usd") if plan else "usd"
        new_end = now + timedelta(days=30)
        await db.subscriptions.update_one(
            {"_id": sub["_id"]},
            {"$set": {"current_period_start": now, "current_period_end": new_end, "updated_at": now}},
        )
        await insert_transaction(
            db,
            user_id=sub["user_id"],
            subscription_id=str(sub["_id"]),
            amount=price,
            currency=currency,
            status=TransactionStatus.COMPLETED,
            provider="mock_auto_renew",
            metadata={"note": "Auto-renewal invoice (mock)"},
        )
        renewed += 1
    return renewed
