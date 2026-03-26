"""
Authentication: register, login, JWT issuance.
"""

from fastapi import APIRouter, HTTPException, status
from pymongo.errors import PyMongoError

from app.api.deps import DbDep
from app.api.serializers import serialize_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.domain import UserRole
from app.repositories import user_repository
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(payload: UserCreate, db: DbDep):
    """Create account; default role seeker unless admin promotes later."""
    if payload.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin accounts cannot be self-registered")
    email = payload.email.lower().strip()
    try:
        if await user_repository.find_by_email(db, email):
            raise HTTPException(status_code=400, detail="Email already registered")
        doc = {
            "email": email,
            "password_hash": hash_password(payload.password),
            "full_name": payload.full_name.strip(),
            "role": payload.role.value,
            "phone": payload.phone,
        }
        uid = await user_repository.insert_user(db, doc)
        created = await user_repository.find_by_id(db, uid)
    except HTTPException:
        raise
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Start MongoDB (port 27017) or set MONGODB_URI, then retry.",
        ) from exc
    if not created:
        raise HTTPException(status_code=500, detail="Registration failed")
    return serialize_user(created)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: DbDep):
    """Return JWT for valid credentials."""
    email = payload.email.lower().strip()
    try:
        user = await user_repository.find_by_email(db, email)
    except PyMongoError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Start MongoDB (port 27017) or set MONGODB_URI, then retry.",
        ) from exc
    ph = user.get("password_hash") if user else None
    if not user or not ph or not verify_password(payload.password, ph):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account disabled")
    token = create_access_token(
        str(user["_id"]),
        extra_claims={"role": user["role"], "email": user["email"]},
    )
    return TokenResponse(access_token=token)
