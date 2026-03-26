"""
RealStat FastAPI application entrypoint.
Wires routers, CORS, static media, Mongo indexes, and WebSocket chat.
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    admin,
    analytics,
    auth,
    favorites,
    listing_alerts,
    messages,
    notifications,
    properties,
    search,
    subscriptions,
    upload,
    users,
)
from app.config import get_settings
from app.core.security import decode_token
from app.database import ensure_indexes, get_database
from app.repositories import user_repository
from app.ws.manager import manager as ws_manager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: indexes. Shutdown: optional cleanup."""
    Path(settings.LOCAL_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    if os.getenv("REALSTAT_SKIP_DB_INIT") != "1":
        try:
            await ensure_indexes()
        except Exception as exc:
            logging.getLogger("uvicorn.error").warning(
                "MongoDB unavailable; indexes not created (%s). Start MongoDB and restart.",
                exc,
            )
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = settings.API_V1_PREFIX
app.include_router(auth.router, prefix=api)
app.include_router(users.router, prefix=api)
app.include_router(search.router, prefix=api)
app.include_router(properties.router, prefix=api)
app.include_router(admin.router, prefix=api)
app.include_router(subscriptions.router, prefix=api)
app.include_router(messages.router, prefix=api)
app.include_router(upload.router, prefix=api)
app.include_router(notifications.router, prefix=api)
app.include_router(analytics.router, prefix=api)
app.include_router(favorites.router, prefix=api)
app.include_router(listing_alerts.router, prefix=api)

# Local media — directory must exist before StaticFiles mounts (runs at import, before lifespan).
Path(settings.LOCAL_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.LOCAL_UPLOAD_DIR), name="media")


@app.get("/health")
async def health():
    """Load balancer probe."""
    return {"status": "ok"}


async def _user_from_ws_token(token: str) -> dict | None:
    """Validate JWT from query string for WebSocket upgrade."""
    try:
        payload = decode_token(token)
        uid = payload.get("sub")
        if not uid:
            return None
        db = get_database()
        user = await user_repository.find_by_id(db, uid)
        return user
    except Exception:
        return None


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
    """
    Real-time chat channel. Client sends JSON:
    - {"action":"join","conversation_id":"propId:userA:userB"}
    - {"action":"leave","conversation_id":"..."}
    Server pushes {"type":"message","payload":{...}} from REST fan-out.
    """
    user = await _user_from_ws_token(token)
    if not user or not user.get("is_active", True):
        await websocket.close(code=4401)
        return
    uid = str(user["_id"])
    await ws_manager.connect_user(uid, websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            action = data.get("action")
            conv = data.get("conversation_id")
            if action == "join" and conv:
                parts = conv.split(":")
                if len(parts) == 3 and uid in (parts[1], parts[2]):
                    ws_manager.join_conversation(uid, conv)
                    await websocket.send_json({"type": "joined", "conversation_id": conv})
            elif action == "leave" and conv:
                ws_manager.leave_conversation(uid, conv)
                await websocket.send_json({"type": "left", "conversation_id": conv})
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect_user(uid, websocket)


@app.websocket("/ws/admin/monitor")
async def websocket_admin_monitor(websocket: WebSocket, token: str = Query(...)):
    """Admin-only stream of chat events (monitor flag)."""
    user = await _user_from_ws_token(token)
    if not user or user.get("role") != "admin":
        await websocket.close(code=4403)
        return
    await ws_manager.connect_admin_monitor(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive; ignore client messages
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect_user(str(user["_id"]), websocket)
