"""Seeker favorites (saved listings)."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import DbDep, SeekerUser, get_current_user_optional
from app.api.serializers import serialize_property
from app.repositories import favorites_repository
from app.schemas.user import FavoriteBody

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("/status/{property_id}", response_model=dict)
async def favorite_status(
    db: DbDep,
    property_id: str,
    user: Annotated[Optional[dict], Depends(get_current_user_optional)],
):
    if not user or user.get("role") != "seeker":
        return {"favorited": False}
    ok = await favorites_repository.is_favorite(db, str(user["_id"]), property_id)
    return {"favorited": ok}


@router.get("", response_model=dict)
async def list_favorites(db: DbDep, user: SeekerUser, skip: int = 0, limit: int = 50):
    items, total = await favorites_repository.list_favorite_properties(db, str(user["_id"]), skip=skip, limit=limit)
    return {
        "items": [serialize_property(x).model_dump() for x in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("", response_model=dict)
async def add_favorite_route(db: DbDep, user: SeekerUser, body: FavoriteBody):
    ok = await favorites_repository.add_favorite(db, str(user["_id"]), body.property_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Listing not found or not available")
    return {"ok": True}


@router.delete("/{property_id}", response_model=dict)
async def remove_favorite_route(db: DbDep, user: SeekerUser, property_id: str):
    ok = await favorites_repository.remove_favorite(db, str(user["_id"]), property_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"ok": True}
