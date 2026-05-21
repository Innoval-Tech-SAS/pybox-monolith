import redis.asyncio as aioredis

from config.redis_config import RedisConfig


class RedisClient:
    def __init__(self, config: RedisConfig | None = None):
        cfg = config or RedisConfig()
        self._client: aioredis.Redis = aioredis.from_url(cfg.url, decode_responses=True)

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        await self._client.set(key, value, ex=ttl_seconds)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def close(self) -> None:
        await self._client.aclose()


redis_client = RedisClient()
