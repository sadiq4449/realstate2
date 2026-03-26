"""
Subscription plans, checkout (mock / Stripe), invoices, auto-renew tick.
"""

from fastapi import APIRouter, HTTPException

from app.api.deps import AdminUser, CurrentUser, DbDep, OwnerUser
from app.api.serializers import serialize_plan, serialize_subscription, serialize_transaction
from app.config import get_settings
from app.models.domain import TransactionStatus, UserRole
from app.repositories import notification_repository, subscription_repository
from app.schemas.subscription import PlanCreate, PlanOut, PlanUpdate, SubscribeRequest, SubscriptionOut

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans")
async def list_plans_public(db: DbDep):
    """Active plans for pricing page."""
    rows = await subscription_repository.list_plans(db, active_only=True)
    return [serialize_plan(r).model_dump() for r in rows]


@router.post("/plans", response_model=PlanOut)
async def create_plan(payload: PlanCreate, db: DbDep, admin: AdminUser):
    """Admin creates plan."""
    doc = payload.model_dump()
    pid = await subscription_repository.insert_plan(db, doc)
    row = await subscription_repository.get_plan(db, pid)
    await notification_repository.insert_admin_log(
        db,
        admin_id=str(admin["_id"]),
        action="plan_create",
        target_type="plan",
        target_id=pid,
        detail={},
    )
    return serialize_plan(row)


@router.patch("/plans/{plan_id}", response_model=PlanOut)
async def update_plan_route(plan_id: str, payload: PlanUpdate, db: DbDep, admin: AdminUser):
    """Admin updates pricing."""
    patch = payload.model_dump(exclude_unset=True)
    ok = await subscription_repository.update_plan(db, plan_id, patch)
    if not ok:
        raise HTTPException(404, "Plan not found")
    row = await subscription_repository.get_plan(db, plan_id)
    return serialize_plan(row)


@router.get("/me", response_model=SubscriptionOut | dict)
async def my_subscription(db: DbDep, user: CurrentUser):
    """Current owner's subscription."""
    if user.get("role") != UserRole.OWNER.value:
        return {}
    sub = await subscription_repository.get_active_subscription(db, str(user["_id"]))
    if not sub:
        return {}
    return serialize_subscription(sub)


@router.post("/subscribe", response_model=dict)
async def subscribe(payload: SubscribeRequest, db: DbDep, user: OwnerUser):
    """
    Mock payment completes immediately. If STRIPE_SECRET_KEY is set and use_mock_payment is false,
    creates a placeholder Stripe subscription (requires frontend Payment Element in production).
    """
    plan = await subscription_repository.get_plan(db, payload.plan_id)
    if not plan or not plan.get("active", True):
        raise HTTPException(404, "Plan not available")

    settings = get_settings()
    stripe_sub_id = None
    provider = "mock"

    if not payload.use_mock_payment and settings.STRIPE_SECRET_KEY:
        try:
            import stripe

            stripe.api_key = settings.STRIPE_SECRET_KEY
            # Placeholder: real flow needs Customer + PaymentMethod on client
            stripe_sub_id = "stripe_stub_" + payload.plan_id[:8]
            provider = "stripe"
        except Exception as exc:
            raise HTTPException(502, f"Stripe error: {exc}") from exc

    sub_id = await subscription_repository.upsert_user_subscription(
        db,
        str(user["_id"]),
        payload.plan_id,
        stripe_sub_id=stripe_sub_id,
    )

    tid = await subscription_repository.insert_transaction(
        db,
        user_id=str(user["_id"]),
        subscription_id=sub_id,
        amount=float(plan["price_monthly"]),
        currency=plan.get("currency", "usd"),
        status=TransactionStatus.COMPLETED,
        provider=provider,
        metadata={"plan_id": payload.plan_id, "mock": payload.use_mock_payment},
    )

    await notification_repository.insert_notification(
        db,
        user_id=str(user["_id"]),
        title="Subscription active",
        body=f"Plan {plan['name']} is now active.",
        data={"subscription_id": sub_id},
    )

    sub = await subscription_repository.get_active_subscription(db, str(user["_id"]))
    return {
        "subscription": serialize_subscription(sub).model_dump() if sub else None,
        "transaction_id": tid,
    }


@router.get("/invoices", response_model=dict)
async def list_invoices(db: DbDep, user: CurrentUser, skip: int = 0, limit: int = 50):
    """Owner billing history."""
    if user.get("role") != UserRole.OWNER.value:
        return {"items": [], "total": 0}
    items, total = await subscription_repository.list_transactions_for_user(
        db, str(user["_id"]), skip=skip, limit=limit
    )
    return {
        "items": [serialize_transaction(x).model_dump() for x in items],
        "total": total,
    }


@router.post("/system/auto-renew-run")
async def auto_renew_run(db: DbDep, admin: AdminUser):
    """
    Cron-style endpoint: extend mock subscriptions and emit invoices.
    Protect in production with internal secret header if needed.
    """
    n = await subscription_repository.run_auto_renewal_tick(db)
    return {"renewed": n}
