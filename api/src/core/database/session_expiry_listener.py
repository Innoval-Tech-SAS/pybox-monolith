"""Escucha los eventos de expiración de sesión en Redis y cierra la sesión."""

import asyncio
import uuid

from core.config.logger import logger
from core.database.advisory_lock import try_advisory_lock
from core.database.database import db
from core.database.redis import redis_client, redis_factory
from identity.users.repository.user_repository import UserRepository
from identity.users.schemas.user_session_schema import SESSION_KEY_PREFIX, session_key

_KEYEVENT_CHANNEL = "__keyevent@0__:expired"
_RESUBSCRIBE_BACKOFF_SECONDS = 5


async def _mark_user_logged_out(user_id: uuid.UUID) -> None:
    async with try_advisory_lock(f"session_expiry:{user_id}") as acquired:
        if not acquired:
            # Otro worker ya está procesando esta misma expiración: Redis pub/sub
            # entrega el evento a TODOS los suscriptores (uno por worker de uvicorn),
            # no lo reparte como una cola.
            return

        # El usuario pudo volver a iniciar sesión entre que la key expiró en Redis y
        # que este evento se procesó (latencia de red/GC). Si la key ya existe de
        # nuevo, la sesión activa recién creada no debe pisarse.
        if await redis_client.get(session_key(user_id)) is not None:
            return

        async with db.get_session() as session:
            repo = UserRepository(session)
            user = await repo.get_by_id(user_id)
            if user:
                setattr(user, "is_active_sessions", False)
                await repo.update(user)


async def _listen(event_client) -> None:
    await event_client.subscribe(_KEYEVENT_CHANNEL)
    async for message in event_client.listen():
        key: str = message["data"]
        if not key.startswith(SESSION_KEY_PREFIX):
            continue
        try:
            user_id = uuid.UUID(key.removeprefix(SESSION_KEY_PREFIX))
            await _mark_user_logged_out(user_id)
        except Exception:
            logger.exception("session expiry handler failed for key=%s", key)


async def _listen_forever() -> None:
    # Si la conexión de pub/sub se cae (reinicio de Redis, blip de red), `.listen()`
    # lanza y sin este loop la tarea moriría en silencio: el timeout de sesión por
    # inactividad dejaría de funcionar hasta reiniciar el proceso. Se reintenta con
    # una conexión nueva en vez de propagar el error hacia afuera.
    while True:
        try:
            event_client = redis_factory.pubsub_client()
            await _listen(event_client)
        except Exception:
            logger.exception(
                "session expiry listener perdió la conexión, reintentando en %ds",
                _RESUBSCRIBE_BACKOFF_SECONDS,
            )
            await asyncio.sleep(_RESUBSCRIBE_BACKOFF_SECONDS)


async def start_session_expiry_listener() -> asyncio.Task:
    # Requires notify-keyspace-events to include "E" (keyevent) and "x" (expiry).
    # "Ex" enables both. Some managed Redis instances block CONFIG SET — in that
    # case enable it server-side via redis.conf instead.
    await redis_client.config_set("notify-keyspace-events", "Ex")
    return asyncio.create_task(_listen_forever())
