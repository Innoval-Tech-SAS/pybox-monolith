import asyncio

from core.config.logger import logger
from core.database.database import db
from core.database.redis import redis_client, redis_factory
from identity.users.repository.user_repository import UserRepository
from identity.users.schemas.user_session_schema import SESSION_KEY_PREFIX


_KEYEVENT_CHANNEL = "__keyevent@0__:expired"


async def _mark_user_logged_out(user_id: int) -> None:
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
            user_id = int(key.removeprefix(SESSION_KEY_PREFIX))
            await _mark_user_logged_out(user_id)
        except Exception:
            logger.exception("session expiry handler failed for key=%s", key)


async def start_session_expiry_listener() -> asyncio.Task:
    # Requires notify-keyspace-events to include "K" (keyspace) and "x" (expiry).
    # "Ex" enables both. Some managed Redis instances block CONFIG SET — in that
    # case enable it server-side via redis.conf instead.
    await redis_client.config_set("notify-keyspace-events", "Ex")
    event_client = redis_factory.pubsub_client()
    return asyncio.create_task(_listen(event_client))
