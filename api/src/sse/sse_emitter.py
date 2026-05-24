import asyncio
from collections import defaultdict


class SSEEmitter:
    def __init__(self) -> None:
        self._queues: dict[int, list[asyncio.Queue]] = defaultdict(list)

    def subscribe(self, user_id: int) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._queues[user_id].append(q)
        return q

    def unsubscribe(self, user_id: int, queue: asyncio.Queue) -> None:
        queues = self._queues.get(user_id, [])
        if queue in queues:
            queues.remove(queue)
        if not queues:
            self._queues.pop(user_id, None)

    async def emit(self, user_id: int, event: str, data: dict) -> None:
        for q in list(self._queues.get(user_id, [])):
            await q.put({"event": event, "data": data})


sse_emitter = SSEEmitter()
