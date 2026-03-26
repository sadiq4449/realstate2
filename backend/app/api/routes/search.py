"""
Property search: filters, keyword, optional map radius.
"""

from typing import Optional

from fastapi import APIRouter, Query

from app.api.deps import DbDep
from app.api.serializers import serialize_property
from app.models.domain import PropertyStatus
from app.repositories import property_repository

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/properties")
async def search_properties(
    db: DbDep,
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_bedrooms: Optional[int] = None,
    max_bedrooms: Optional[int] = None,
    min_bathrooms: Optional[int] = None,
    furnished: Optional[bool] = None,
    amenities: Optional[str] = Query(None, description="Comma-separated amenities"),
    city: Optional[str] = None,
    near_lat: Optional[float] = None,
    near_lng: Optional[float] = None,
    radius_m: Optional[float] = Query(None, description="Meters for $nearSphere"),
    skip: int = 0,
    limit: int = 20,
):
    """
    Full-text + structured filters. When near_lat/near_lng + radius_m set, applies geo filter.
    """
    amen_list = [a.strip() for a in amenities.split(",")] if amenities else None
    if amen_list == []:
        amen_list = None

    max_dist = radius_m if (near_lat is not None and near_lng is not None and radius_m) else None

    items, total = await property_repository.search_properties(
        db,
        q=q,
        min_price=min_price,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        max_bedrooms=max_bedrooms,
        min_bathrooms=min_bathrooms,
        furnished=furnished,
        amenities=amen_list,
        city=city,
        status=PropertyStatus.APPROVED,
        near_lng=near_lng,
        near_lat=near_lat,
        max_distance_m=max_dist,
        skip=skip,
        limit=limit,
    )
    return {
        "items": [serialize_property(x).model_dump() for x in items],
        "total": total,
        "skip": skip,
        "limit": limit,
    }
