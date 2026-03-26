"""
Current user profile and admin user management.
"""

from fastapi import APIRouter, HTTPException

from app.api.deps import AdminUser, CurrentUser, DbDep
from app.api.serializers import serialize_user
from app.models.domain import UserRole
from app.repositories import notification_repository, user_repository
from app.schemas.user import AdminUserUpdate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser, db: DbDep):
    """Authenticated profile."""
    doc = await user_repository.find_by_id(db, str(user["_id"]))
    if not doc:
        raise HTTPException(404, "User not found")
    return serialize_user(doc)


@router.patch("/me", response_model=UserOut)
async def update_me(payload: UserUpdate, user: CurrentUser, db: DbDep):
    """Update own profile fields."""
    patch = payload.model_dump(exclude_unset=True)
    if not patch:
        return serialize_user(user)
    await user_repository.update_user(db, str(user["_id"]), patch)
    doc = await user_repository.find_by_id(db, str(user["_id"]))
    return serialize_user(doc)


@router.get("/admin/list", response_model=dict)
async def admin_list_users(
    db: DbDep,
    admin: AdminUser,
    role: UserRole | None = None,
    skip: int = 0,
    limit: int = 50,
):
    """Paginated users for super admin."""
    items, total = await user_repository.list_users(db, role=role, skip=skip, limit=limit)
    return {
        "items": [serialize_user(x).model_dump() for x in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.patch("/admin/{user_id}", response_model=UserOut)
async def admin_update_user(user_id: str, payload: AdminUserUpdate, db: DbDep, admin: AdminUser):
    """Change role or disable user."""
    patch = payload.model_dump(exclude_unset=True)
    if "role" in patch and patch["role"] is not None:
        patch["role"] = patch["role"].value
    ok = await user_repository.update_user(db, user_id, patch)
    if not ok:
        raise HTTPException(404, "User not found")
    doc = await user_repository.find_by_id(db, user_id)
    if not doc:
        raise HTTPException(404, "User not found")
    await notification_repository.insert_admin_log(
        db,
        admin_id=str(admin["_id"]),
        action="user_update",
        target_type="user",
        target_id=user_id,
        detail=patch,
    )
    if doc:
        await notification_repository.insert_notification(
            db,
            user_id=user_id,
            title="Account updated",
            body="An administrator updated your account settings.",
            data={"patch": patch},
        )
    return serialize_user(doc)
