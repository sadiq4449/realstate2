# MongoDB collections and sample documents

Collections: `users`, `properties`, `subscription_plans`, `subscriptions`, `transactions`, `messages`, `notifications`, `admin_logs`.

Indexes are created on API startup (`ensure_indexes`).

## users

```json
{
  "_id": ObjectId("..."),
  "email": "owner@demo.com",
  "password_hash": "<bcrypt>",
  "full_name": "Demo Owner",
  "role": "owner",
  "phone": "+92-300-0000001",
  "is_active": true,
  "created_at": ISODate("2025-03-01T00:00:00Z")
}
```

## properties

```json
{
  "_id": ObjectId("..."),
  "owner_id": "<string user id>",
  "title": "Clifton Sea View Apartment",
  "description": "3BR near the coast...",
  "city": "Karachi",
  "address": "Block 4 Clifton",
  "rent_monthly": 185000,
  "bedrooms": 3,
  "bathrooms": 3,
  "furnished": true,
  "amenities": ["parking", "security"],
  "images": ["https://..."],
  "status": "approved",
  "location": { "type": "Point", "coordinates": [67.0299, 24.8138] },
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

## subscription_plans

```json
{
  "_id": ObjectId("..."),
  "name": "Pro",
  "description": "Up to 25 listings",
  "price_monthly": 79,
  "currency": "usd",
  "max_listings": 25,
  "features": { "analytics": true },
  "active": true,
  "created_at": ISODate("...")
}
```

## subscriptions

```json
{
  "_id": ObjectId("..."),
  "user_id": "<owner id>",
  "plan_id": "<plan id string>",
  "status": "active",
  "current_period_start": ISODate("..."),
  "current_period_end": ISODate("..."),
  "auto_renew": true,
  "stripe_subscription_id": null,
  "created_at": ISODate("..."),
  "updated_at": ISODate("...")
}
```

## transactions

```json
{
  "_id": ObjectId("..."),
  "user_id": "<owner id>",
  "subscription_id": "<subscription id>",
  "amount": 79,
  "currency": "usd",
  "status": "completed",
  "provider": "mock",
  "invoice_number": "INV-...",
  "metadata": {},
  "created_at": ISODate("...")
}
```

## messages

```json
{
  "_id": ObjectId("..."),
  "conversation_id": "<propertyId>:<userA>:<userB>",
  "property_id": "<property id>",
  "sender_id": "<user id>",
  "recipient_id": "<user id>",
  "body": "Hello",
  "attachment_url": null,
  "created_at": ISODate("...")
}
```

## notifications

```json
{
  "_id": ObjectId("..."),
  "user_id": "<user id>",
  "title": "Listing approved",
  "body": "Your listing is live.",
  "read": false,
  "data": { "property_id": "..." },
  "created_at": ISODate("...")
}
```

## admin_logs

```json
{
  "_id": ObjectId("..."),
  "admin_id": "<admin user id>",
  "action": "property_moderate",
  "target_type": "property",
  "target_id": "<property id>",
  "detail": { "status": "approved" },
  "created_at": ISODate("...")
}
```
