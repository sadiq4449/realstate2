#!/usr/bin/env python3
"""
Seed MongoDB with sample users, plans, properties, and messages.
Run from repo:  python scripts/seed_mongo.py
Requires MONGODB_URI (default mongodb://localhost:27017) and DB realstat.
"""

import os
import sys
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import MongoClient
from passlib.context import CryptContext

# Allow running from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGODB_DB", "realstat")


def main() -> None:
    client = MongoClient(URI)
    db = client[DB_NAME]
    now = datetime.now(timezone.utc)
    h = lambda p: pwd_context.hash(p)  # noqa: E731

    db.users.delete_many({"email": {"$in": ["owner@demo.com", "seeker@demo.com", "admin@demo.com"]}})
    db.subscription_plans.delete_many({})
    db.properties.delete_many({})
    db.subscriptions.delete_many({})
    db.transactions.delete_many({})
    db.messages.delete_many({})
    db.notifications.delete_many({})
    db.admin_logs.delete_many({})

    owner_id = ObjectId()
    seeker_id = ObjectId()
    admin_id = ObjectId()

    db.users.insert_many(
        [
            {
                "_id": owner_id,
                "email": "owner@demo.com",
                "password_hash": h("password123"),
                "full_name": "Demo Owner",
                "role": "owner",
                "phone": "+92-300-0000001",
                "is_active": True,
                "created_at": now,
            },
            {
                "_id": seeker_id,
                "email": "seeker@demo.com",
                "password_hash": h("password123"),
                "full_name": "Demo Seeker",
                "role": "seeker",
                "phone": "+92-300-0000002",
                "is_active": True,
                "created_at": now,
            },
            {
                "_id": admin_id,
                "email": "admin@demo.com",
                "password_hash": h("admin12345"),
                "full_name": "Super Admin",
                "role": "admin",
                "phone": "+92-300-0000000",
                "is_active": True,
                "created_at": now,
            },
        ]
    )

    plan_basic = ObjectId()
    plan_pro = ObjectId()
    db.subscription_plans.insert_many(
        [
            {
                "_id": plan_basic,
                "name": "Basic",
                "description": "Up to 5 active listings",
                "price_monthly": 29.0,
                "currency": "usd",
                "max_listings": 5,
                "features": {"analytics": False, "priority": False},
                "active": True,
                "created_at": now,
            },
            {
                "_id": plan_pro,
                "name": "Pro",
                "description": "Up to 25 listings + analytics",
                "price_monthly": 79.0,
                "currency": "usd",
                "max_listings": 25,
                "features": {"analytics": True, "priority": True},
                "active": True,
                "created_at": now,
            },
        ]
    )

    prop1 = ObjectId()
    prop2 = ObjectId()
    db.properties.insert_many(
        [
            {
                "_id": prop1,
                "owner_id": str(owner_id),
                "title": "Clifton Sea View Apartment",
                "description": "3BR near the coast with parking and security. Near Dolmen Mall.",
                "city": "Karachi",
                "address": "Block 4 Clifton",
                "rent_monthly": 185000,
                "bedrooms": 3,
                "bathrooms": 3,
                "furnished": True,
                "amenities": ["parking", "security", "elevator", "ac"],
                "images": [
                    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800",
                    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800",
                ],
                "status": "approved",
                "location": {"type": "Point", "coordinates": [67.0299, 24.8138]},
                "created_at": now,
                "updated_at": now,
            },
            {
                "_id": prop2,
                "owner_id": str(owner_id),
                "title": "DHA Phase 6 Townhouse",
                "description": "4BR corner unit, lawn, ideal for families.",
                "city": "Karachi",
                "address": "Phase 6 DHA",
                "rent_monthly": 320000,
                "bedrooms": 4,
                "bathrooms": 4,
                "furnished": False,
                "amenities": ["parking", "garden", "security"],
                "images": [
                    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800",
                ],
                "status": "pending",
                "location": {"type": "Point", "coordinates": [67.0752, 24.8134]},
                "created_at": now,
                "updated_at": now,
            },
        ]
    )

    conv = f"{prop1}:{min(str(owner_id), str(seeker_id))}:{max(str(owner_id), str(seeker_id))}"
    db.messages.insert_one(
        {
            "conversation_id": conv,
            "property_id": str(prop1),
            "sender_id": str(seeker_id),
            "recipient_id": str(owner_id),
            "body": "Hi, is this still available for June?",
            "attachment_url": None,
            "created_at": now,
        }
    )

    db.notifications.insert_one(
        {
            "user_id": str(owner_id),
            "title": "New message",
            "body": "A seeker contacted you about Clifton Sea View Apartment.",
            "read": False,
            "data": {"property_id": str(prop1)},
            "created_at": now,
        }
    )

    print("Seed complete.")
    print("  owner@demo.com / password123")
    print("  seeker@demo.com / password123")
    print("  admin@demo.com / admin12345")


if __name__ == "__main__":
    main()
