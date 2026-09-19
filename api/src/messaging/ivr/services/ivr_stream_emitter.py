"""Fan-out en tiempo real de los eventos IVR hacia el frontend (SSE).

Por qué no se reusa `core/sse/sse_emitter.py` tal cual: aquel indexa las colas
por `user_id`, y el monitor necesita emitir "a todos los que están mirando la
campaña X". Este emisor es el mismo patrón pero indexado por **tópico**, y vive
en el módulo IVR para dejar aislado el punto exacto donde habrá que introducir
un `RedisSSEEmitter` el día que la API corra con más de un worker (hoy el
`Dockerfile` arranca `uvicorn` sin `--workers`, la misma suposición que ya hacen
el chat y las notificaciones).

Ver `.claude/plans/ivr-helena/03-arquitectura-realtime.md`.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from collections import defaultdict
from typing import Any

from core.config.logger import logger

#: Tope de eventos encolados por suscriptor. Si un cliente deja de consumir, se
#: descarta el evento más viejo en vez de crecer sin límite: el monitor siempre
#: puede reconstruir el estado real pidiendo el snapshot.
_MAX_QUEUE_SIZE = 200


def campaign_topic(campaign_id: uuid.UUID | str) -> str:
    return f"campaign:{campaign_id}"


def organization_topic(organization_id: uuid.UUID | str) -> str:
    return f"org:{organization_id}"


class IvrStreamEmitter:

    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = defaultdict(list)

    # ── Suscripción ───────────────────────────────────────────────────────────

    def subscribe(self, topic: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=_MAX_QUEUE_SIZE)
        self._queues[topic].append(queue)
        return queue

    def unsubscribe(self, topic: str, queue: asyncio.Queue) -> None:
        queues = self._queues.get(topic, [])
        if queue in queues:
            queues.remove(queue)
        if not queues:
            self._queues.pop(topic, None)

    def subscriber_count(self, topic: str) -> int:
        return len(self._queues.get(topic, []))

    # ── Emisión ───────────────────────────────────────────────────────────────

    async def emit(self, topic: str, event: str, data: dict[str, Any]) -> None:
        queues = self._queues.get(topic)
        if not queues:
            return

        payload = {"event": event, "data": json.dumps(data, default=str)}
        for queue in list(queues):
            self._put_nowait_dropping_oldest(queue, payload, topic)

    async def emit_many(self, topics: list[str | None], event: str, data: dict[str, Any]) -> None:
        """Emite el mismo evento a varios tópicos (campaña + organización)."""
        for topic in topics:
            if topic:
                await self.emit(topic, event, data)

    def _put_nowait_dropping_oldest(
        self, queue: asyncio.Queue, payload: dict[str, str], topic: str
    ) -> None:
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            try:
                queue.get_nowait()
                queue.put_nowait(payload)
                logger.warning(
                    "[ivr_stream] cola llena en topic=%s: se descartó el evento más viejo", topic
                )
            except (asyncio.QueueEmpty, asyncio.QueueFull):
                logger.warning("[ivr_stream] no se pudo encolar el evento en topic=%s", topic)


#: Instancia de proceso. Ver la nota de multi-worker en el docstring del módulo.
ivr_stream = IvrStreamEmitter()


# ── Eventos del dominio ───────────────────────────────────────────────────────

EVENT_CALL_UPDATED = "ivr:call-updated"
EVENT_STATS_UPDATED = "ivr:stats-updated"
EVENT_CAMPAIGN_STATUS = "ivr:campaign-status"
EVENT_HEARTBEAT = "ivr:heartbeat"
