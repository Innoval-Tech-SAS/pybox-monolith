import json
from typing import Any, Type, TypeVar

import redis.asyncio as aioredis
from pydantic import BaseModel

from config.redis_config import RedisConfig

T = TypeVar("T")


class RedisClient:
    def __init__(self, config: RedisConfig = RedisConfig()):
        cfg = config
        self._client: aioredis.Redis = aioredis.from_url(cfg.url, decode_responses=True)

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
        serialized = value.model_dump_json() if isinstance(value, BaseModel) else json.dumps(value)
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

    async def close(self) -> None:
        await self._client.aclose()


redis_client = RedisClient()
