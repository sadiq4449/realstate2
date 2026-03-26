"""
FastAPI dependencies: DB session, current user, role guards.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.security import decode_token
from app.database import get_database
from app.models.domain import UserRole
from app.repositories import user_repository

security = HTTPBearer(auto_error=False)


async def get_db():
    """Yield Mongo database handle."""
    yield get_database()


DbDep = Annotated[object, Depends(get_db)]


async def get_current_user_optional(
    creds: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: DbDep,
):
    """Return user dict if Bearer token valid, else None."""
    if creds is None or not creds.credentials:
        return None
    try:
        payload = decode_token(creds.credentials)
        uid = payload.get("sub")
        if not uid:
            return None
        user = await user_repository.find_by_id(db, uid)
        return user
    except JWTError:
        return None


async def get_current_user(
    user: Annotated[Optional[dict], Depends(get_current_user_optional)],
):
    """Require authenticated user."""
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def require_roles(*roles: UserRole):
    """Factory for role-based access."""

    async def _inner(user: Annotated[dict, Depends(get_current_user)]):
        r = user.get("role")
        allowed = {x.value for x in roles}
        if r not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return _inner


CurrentUser = Annotated[dict, Depends(get_current_user)]
OwnerUser = Annotated[dict, Depends(require_roles(UserRole.OWNER))]
SeekerUser = Annotated[dict, Depends(require_roles(UserRole.SEEKER))]
AdminUser = Annotated[dict, Depends(require_roles(UserRole.ADMIN))]
