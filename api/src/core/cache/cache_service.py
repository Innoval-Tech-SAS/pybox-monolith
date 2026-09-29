"""Servicio de cache-aside genérico sobre Redis."""

from collections.abc import Awaitable, Callable
from typing import TypeVar

from pydantic import TypeAdapter

from core.database.redis import redis_client

T = TypeVar("T")

_DEFAULT_TTL = 300


class CacheService:
    """Cache-aside respaldado por Redis.

    Serializa y deserializa cualquier tipo compatible con Pydantic (modelos,
    listas, primitivos) usando TypeAdapter, lo que permite cachear respuestas
    complejas sin depender de la sesión de SQLAlchemy.

    Uso básico:
        _adapter = TypeAdapter(list[PortfolioResponse])

        result = await cache.get_or_set(
            key=f"portfolio:list:{org_id}",
            fetch=lambda: service.list_portfolios(org_id),
            adapter=_adapter,
            ttl=120,
        )
        await cache.bust(f"portfolio:list:{org_id}")

    Convención de keys: ``{dominio}:{operación}:{identificador}``
    """

    async def get_or_set(
        self,
        key: str,
        fetch: Callable[[], Awaitable[T]],
        adapter: TypeAdapter[T],
        ttl: int = _DEFAULT_TTL,
    ) -> T:
        raw = await redis_client.get(key)
        if raw is not None:
            return adapter.validate_json(raw)
        result = await fetch()
        await redis_client.set(key, adapter.dump_json(result).decode(), ttl)
        return result

    async def bust(self, *keys: str) -> None:
        """Invalida keys exactas."""
        for key in keys:
            await redis_client.delete(key)

    async def bust_prefix(self, prefix: str) -> None:
        """Invalida todas las keys que empiezan con ``prefix:`` usando SCAN."""
        await redis_client.delete_by_pattern(f"{prefix}:*")


cache_service = CacheService()
