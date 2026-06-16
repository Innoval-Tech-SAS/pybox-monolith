import uuid
from collections import defaultdict

from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[uuid.UUID, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: uuid.UUID, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[user_id].append(ws)

    def disconnect(self, user_id: uuid.UUID, ws: WebSocket) -> None:
        conns = self._connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)

    def online_user_ids(self) -> set[uuid.UUID]:
        return {uid for uid, conns in self._connections.items() if conns}

    async def broadcast_to_others(self, exclude_user_id: uuid.UUID, event: str, data: dict) -> None:
        for uid in self.online_user_ids():
            if uid != exclude_user_id:
                await self.send_to_user(uid, event, data)

    async def send_to_user(self, user_id: uuid.UUID, event: str, data: dict) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._connections.get(user_id, [])):
            try:
                await ws.send_json({"event": event, "data": data})
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)


ws_manager = ChatConnectionManager()
