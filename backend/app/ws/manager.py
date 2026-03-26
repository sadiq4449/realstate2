"""
In-memory WebSocket connection manager.
Broadcasts chat events to participants; admins can monitor via optional monitor flag.
"""

from typing import Any, Dict, List, Set

from fastapi import WebSocket


class ConnectionManager:
    """Maps user_id -> active websockets and conversation_id -> subscriber user ids."""

    def __init__(self) -> None:
        self.active: Dict[str, List[WebSocket]] = {}
        self.conversation_subs: Dict[str, Set[str]] = {}
        self.admin_monitors: List[WebSocket] = []

    async def connect_user(self, user_id: str, websocket: WebSocket) -> None:
        """Register authenticated user socket."""
        await websocket.accept()
        self.active.setdefault(user_id, []).append(websocket)

    def disconnect_user(self, user_id: str, websocket: WebSocket) -> None:
        """Remove socket from user bucket."""
        if user_id in self.active:
            self.active[user_id] = [w for w in self.active[user_id] if w is not websocket]
            if not self.active[user_id]:
                del self.active[user_id]
        if websocket in self.admin_monitors:
            self.admin_monitors.remove(websocket)

    async def connect_admin_monitor(self, websocket: WebSocket) -> None:
        """Admin read-only tap for moderation dashboards."""
        await websocket.accept()
        self.admin_monitors.append(websocket)

    def join_conversation(self, user_id: str, conversation_id: str) -> None:
        """Track interest in a thread for routing."""
        self.conversation_subs.setdefault(conversation_id, set()).add(user_id)

    def leave_conversation(self, user_id: str, conversation_id: str) -> None:
        if conversation_id in self.conversation_subs:
            self.conversation_subs[conversation_id].discard(user_id)

    async def send_to_user(self, user_id: str, payload: Dict[str, Any]) -> None:
        """Push JSON-serializable event to all tabs of a user."""
        for ws in list(self.active.get(user_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                continue

    async def broadcast_conversation(
        self, conversation_id: str, payload: Dict[str, Any], exclude_user: str | None = None
    ) -> None:
        """Notify all users subscribed to conversation."""
        users = list(self.conversation_subs.get(conversation_id, set()))
        for uid in users:
            if exclude_user and uid == exclude_user:
                continue
            await self.send_to_user(uid, payload)

    async def broadcast_admins(self, payload: Dict[str, Any]) -> None:
        """Fan-out to monitoring admins."""
        for ws in list(self.admin_monitors):
            try:
                await ws.send_json(payload)
            except Exception:
                continue


manager = ConnectionManager()
