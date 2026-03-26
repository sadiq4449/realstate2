"""
Sample automated tests (integration when Mongo is up).
Ten scenarios are also documented in ../../docs/TEST_CASES.md.
"""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio


async def test_health():
    """1) API process responds on /health."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


@pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION") == "1",
    reason="SKIP_INTEGRATION=1",
)
async def test_register_login_flow(mongo_available):
    """2) Register seeker + login returns JWT (needs Mongo)."""
    if not mongo_available:
        pytest.skip("MongoDB not available")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        email = "pytest_seeker@example.com"
        reg = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "pytestpass123",
                "full_name": "Py Seeker",
                "role": "seeker",
            },
        )
        assert reg.status_code in (200, 400)
        if reg.status_code == 400:
            pytest.skip("User may already exist from prior run")
        log = await ac.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "pytestpass123"},
        )
        assert log.status_code == 200
        assert "access_token" in log.json()


@pytest.mark.skipif(
    os.environ.get("REALSTAT_SKIP_DB_INIT") == "1",
    reason="Search needs DB indexes + connection; unset REALSTAT_SKIP_DB_INIT and run Mongo",
)
async def test_search_validation():
    """3) Search endpoint returns JSON list shape."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/search/properties", params={"limit": 5})
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert "total" in body


def test_password_hash_roundtrip():
    """4) Password hashing verifies."""
    from app.core.security import hash_password, verify_password

    h = hash_password("secret123")
    assert verify_password("secret123", h)
    assert not verify_password("wrong", h)


def test_conversation_id_stable():
    """5) Conversation id is deterministic."""
    from app.repositories.message_repository import make_conversation_id

    a = make_conversation_id("p1", "u2", "u1")
    b = make_conversation_id("p1", "u1", "u2")
    assert a == b


def test_jwt_contains_sub():
    """6) JWT encodes subject."""
    from app.core.security import create_access_token, decode_token

    t = create_access_token("user123", extra_claims={"role": "seeker"})
    p = decode_token(t)
    assert p["sub"] == "user123"
    assert p["role"] == "seeker"


def test_property_status_enum():
    """7) Property status values."""
    from app.models.domain import PropertyStatus

    assert PropertyStatus.APPROVED.value == "approved"


def test_user_role_enum():
    """8) User roles include admin."""
    from app.models.domain import UserRole

    assert UserRole.ADMIN.value == "admin"


def test_plan_schema():
    """9) PlanCreate validates price."""
    from pydantic import ValidationError

    from app.schemas.subscription import PlanCreate

    PlanCreate(name="X", price_monthly=10, max_listings=3)
    with pytest.raises(ValidationError):
        PlanCreate(name="X", price_monthly=-1, max_listings=3)


def test_geo_point_schema():
    """10) GeoPoint builds coordinates list."""
    from app.schemas.property import GeoPoint

    g = GeoPoint(coordinates=[67.0, 24.8])
    assert g.type == "Point"
    assert len(g.coordinates) == 2
