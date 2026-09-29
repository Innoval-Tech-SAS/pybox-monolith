import json
from typing import Any, AsyncGenerator, Type, TypeVar

import redis.asyncio as aioredis
from pydantic import BaseModel
from redis.asyncio.client import PubSub

from core.config.redis_config import RedisConfig

T = TypeVar("T")


class RedisClient:
    """get/set client — uses a single shared connection."""

    def __init__(self, config: RedisConfig = RedisConfig()):
        self._client: aioredis.Redis = aioredis.from_url(
            config.url, decode_responses=True
        )

    @classmethod
    def get_instance(cls) -> "RedisClient":
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    async def set(
        self, key: str, value: str, ttl_seconds: int = RedisConfig.DEFAULT_TTL
    ) -> None:
        await self._client.set(key, value, ex=ttl_seconds)

    async def set_json(
        self, key: str, value: Any, ttl_seconds: int = RedisConfig.DEFAULT_TTL
    ) -> None:
        serialized = (
            value.model_dump_json()
            if isinstance(value, BaseModel)
            else json.dumps(value)
        )
        await self._client.set(key, serialized, ex=ttl_seconds)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def get_json(self, key: str, cls: Type[T]) -> T | None:
        raw = await self._client.get(key)
        if raw is None:
            return None
        if issubclass(cls, BaseModel):
            return cls.model_validate_json(raw)  # type: ignore[return-value]
        return json.loads(raw)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def increment(self, key: str, ttl_seconds: int) -> int:
        """Contador de ventana fija: INCR es atómico en Redis; el EXPIRE solo se
        arma en el primer incremento de la ventana para no reiniciar el TTL en
        cada intento. Usado por el rate limiter de endpoints de auth."""
        value: int = await self._client.incr(key)
        if value == 1:
            await self._client.expire(key, ttl_seconds)
        return value

    async def expire(
        self, key: str, ttl_seconds: int = RedisConfig.DEFAULT_TTL
    ) -> None:
        await self._client.expire(key, ttl_seconds)

    async def config_set(self, name: str, value: str) -> None:
        await self._client.config_set(name, value)

    async def delete_by_pattern(self, pattern: str) -> None:
        async for key in self._client.scan_iter(match=pattern):
            await self._client.delete(key)

    async def close(self) -> None:
        await self._client.aclose()


class RedisEventClient:
    """pub/sub client — each instance owns its own connection and pubsub object."""

    def __init__(self, config: RedisConfig = RedisConfig()):
        self._client: aioredis.Redis = aioredis.from_url(
            config.url, decode_responses=True
        )
        self._pubsub: PubSub = self._client.pubsub()

    async def subscribe(self, *channels: str) -> None:
        await self._pubsub.subscribe(*channels)

    async def psubscribe(self, *patterns: str) -> None:
        await self._pubsub.psubscribe(*patterns)

    async def unsubscribe(self, *channels: str) -> None:
        await self._pubsub.unsubscribe(*channels)

    async def listen(self) -> AsyncGenerator[dict, None]:
        async for message in self._pubsub.listen():
            if message["type"] in ("message", "pmessage"):
                yield message

    async def publish(self, channel: str, message: str) -> None:
        await self._client.publish(channel, message)

    async def close(self) -> None:
        await self._pubsub.close()
        await self._client.aclose()


class RedisFactory:
    """Creates typed Redis clients from a shared config."""

    def __init__(self, config: RedisConfig | None = None):
        self._config = config or RedisConfig()
        self._set_client: RedisClient | None = None

    def get_set_client(self) -> RedisClient:
        if self._set_client is None:
            self._set_client = RedisClient(self._config)
        return self._set_client

    def pubsub_client(self) -> RedisEventClient:
        return RedisEventClient(self._config)


redis_factory = RedisFactory()
redis_client = redis_factory.get_set_client()
