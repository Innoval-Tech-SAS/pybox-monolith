from collections import defaultdict

from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[user_id].append(ws)

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        conns = self._connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)

    async def send_to_user(self, user_id: int, event: str, data: dict) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._connections.get(user_id, [])):
            try:
                await ws.send_json({"event": event, "data": data})
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)


ws_manager = ChatConnectionManager()
