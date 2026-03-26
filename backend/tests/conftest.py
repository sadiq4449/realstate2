"""
Pytest fixtures: optional live MongoDB for integration tests.
Set MONGODB_URI for integration; otherwise some tests skip.
"""

import os

# Allow ASGI tests without a live Mongo on developer machines
os.environ.setdefault("REALSTAT_SKIP_DB_INIT", "1")

import pytest


@pytest.fixture(scope="session")
def mongo_available() -> bool:
    """True if MongoDB responds (lightweight check)."""
    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    try:
        from pymongo import MongoClient

        c = MongoClient(uri, serverSelectionTimeoutMS=2000)
        c.admin.command("ping")
        c.close()
        return True
    except Exception:
        return False
