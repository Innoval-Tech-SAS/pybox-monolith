import uuid

from core.database import redis as redis_module
from core.database.redis import redis_client


class TestIncrement:
    """`increment` arma el TTL solo en el primer incremento de la ventana -- así un
    reintento a mitad de ventana no la reinicia. Usado por el rate limiter."""

    async def test_first_increment_sets_ttl(self, fake_redis):
        key = f"rl:{uuid.uuid4()}"
        value = await redis_client.increment(key, ttl_seconds=60)
        assert value == 1
        entry = fake_redis._store[key]
        assert entry[1] is not None  # TTL armado

    async def test_second_increment_does_not_reset_ttl(self, fake_redis):
        key = f"rl:{uuid.uuid4()}"
        await redis_client.increment(key, ttl_seconds=60)
        first_expiry = fake_redis._store[key][1]

        second_value = await redis_client.increment(key, ttl_seconds=999)
        assert second_value == 2
        # El segundo incremento no debió pedir un nuevo TTL: sigue siendo el de la
        # primera llamada (60s), no el de la segunda (999s).
        assert fake_redis._store[key][1] == first_expiry


class TestExpire:
    async def test_expire_updates_ttl_of_existing_key(self, fake_redis):
        key = f"exp:{uuid.uuid4()}"
        await redis_client.set(key, "value", ttl_seconds=5)
        await redis_client.expire(key, ttl_seconds=999)
        # sigue legible (no expiró) y el nuevo TTL quedó registrado
        assert await redis_client.get(key) == "value"
        assert fake_redis._store[key][1] is not None

    async def test_expire_on_missing_key_is_noop(self, fake_redis):
        # No debe crear la key ni lanzar si no existe.
        await redis_client.expire(f"missing:{uuid.uuid4()}", ttl_seconds=60)


class TestDeleteByPattern:
    """`delete_by_pattern` (usado por CacheService.bust_prefix) recorre las keys por
    SCAN y borra las que matchean el prefijo -- deja intactas las demás."""

    async def test_deletes_only_matching_keys(self, fake_redis, monkeypatch):
        prefix = f"portfolio:{uuid.uuid4()}"
        await redis_client.set(f"{prefix}:list:1", "a", ttl_seconds=60)
        await redis_client.set(f"{prefix}:list:2", "b", ttl_seconds=60)
        await redis_client.set("unrelated:key", "c", ttl_seconds=60)

        async def _scan_iter(match: str | None = None):
            pattern = (match or "*").rstrip("*")
            for key in list(fake_redis._store.keys()):
                if key.startswith(pattern):
                    yield key

        monkeypatch.setattr(fake_redis, "scan_iter", _scan_iter, raising=False)

        await redis_client.delete_by_pattern(f"{prefix}:*")

        assert await redis_client.get(f"{prefix}:list:1") is None
        assert await redis_client.get(f"{prefix}:list:2") is None
        assert await redis_client.get("unrelated:key") == "c"


class TestRedisFactory:
    def test_get_set_client_returns_singleton(self):
        factory = redis_module.RedisFactory()
        first = factory.get_set_client()
        second = factory.get_set_client()
        assert first is second

    def test_pubsub_client_returns_new_instance_each_time(self):
        factory = redis_module.RedisFactory()
        first = factory.pubsub_client()
        second = factory.pubsub_client()
        assert first is not second
