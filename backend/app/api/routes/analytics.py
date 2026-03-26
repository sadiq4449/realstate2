"""
Aggregate stats for admin dashboards (charts on frontend).
"""

from fastapi import APIRouter

from app.api.deps import AdminUser, DbDep, OwnerUser
from app.models.domain import PropertyStatus, UserRole
from app.repositories import message_repository, property_repository

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def analytics_summary(db: DbDep, admin: AdminUser):
    """High-level KPIs."""
    users_total = await db.users.count_documents({})
    owners = await db.users.count_documents({"role": UserRole.OWNER.value})
    seekers = await db.users.count_documents({"role": UserRole.SEEKER.value})
    listings = await db.properties.count_documents({})
    approved = await db.properties.count_documents({"status": PropertyStatus.APPROVED.value})
    pending = await db.properties.count_documents({"status": PropertyStatus.PENDING.value})
    subs = await db.subscriptions.count_documents({"status": "active"})
    revenue = await db.transactions.aggregate(
        [
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]
    ).to_list(length=1)
    total_rev = float(revenue[0]["total"]) if revenue else 0.0
    return {
        "users_total": users_total,
        "owners": owners,
        "seekers": seekers,
        "listings_total": listings,
        "listings_approved": approved,
        "listings_pending": pending,
        "active_subscriptions": subs,
        "revenue_completed_total": total_rev,
    }


@router.get("/listings-by-city")
async def listings_by_city(db: DbDep, admin: AdminUser):
    """Bar chart data: count per city."""
    pipeline = [
        {"$match": {"status": PropertyStatus.APPROVED.value}},
        {"$group": {"_id": "$city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 12},
    ]
    rows = await db.properties.aggregate(pipeline).to_list(length=20)
    return [{"city": r["_id"], "count": r["count"]} for r in rows]


@router.get("/owner/summary")
async def owner_performance_summary(db: DbDep, user: OwnerUser):
    """Per-listing views and inquiry (message) counts for owner dashboard."""
    items, total = await property_repository.list_by_owner(db, str(user["_id"]), skip=0, limit=200)
    ids = [str(x["_id"]) for x in items]
    msg_counts = await message_repository.count_messages_by_property_ids(db, ids)
    listings = []
    for it in items:
        pid = str(it["_id"])
        listings.append(
            {
                "property_id": pid,
                "title": it.get("title", ""),
                "status": it.get("status"),
                "view_count": int(it.get("view_count") or 0),
                "inquiries": msg_counts.get(pid, 0),
            }
        )
    return {"listings": listings, "total_listings": total}
