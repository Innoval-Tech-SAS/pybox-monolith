import zlib
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text

from core.database.database import db

# Namespace fijo para separar estos locks de otros usos de advisory locks (ej. el
# pg_advisory_lock de arranque en lifespan.py, que usa la forma de un solo entero).
_NAMESPACE = 42


@asynccontextmanager
async def try_advisory_lock(key: str) -> AsyncGenerator[bool, None]:
    """
    Coordina un job recurrente entre los N workers de uvicorn (`--workers` en el
    Dockerfile): cada worker es un proceso separado que corre su propio scheduler en
    memoria (APScheduler no comparte estado entre procesos), así que todos disparan
    el mismo tick al mismo tiempo sin este lock.

    No bloqueante a propósito: si otro worker ya tiene el lock, más vale saltar este
    tick (`acquired=False`) que esperar y encolarse, duplicando el trabajo apenas se
    libere. `key` se resuelve a un entero vía CRC32 -- determinista entre procesos, a
    diferencia de `hash()` que Python aleatoriza por proceso -- para poder tener un
    lock distinto por job/país sin colisionar entre sí. `pg_try_advisory_lock(int, int)`
    espera enteros CON signo de 32 bits, pero CRC32 devuelve un entero SIN signo de 32
    bits (hasta 4294967295) -- se reinterpreta el bit alto como signo para que siempre
    quepa, en vez de que un país cualquiera tumbe el arranque con "value out of int32
    range".
    """
    unsigned_digest = zlib.crc32(key.encode("utf-8"))
    digest = unsigned_digest - 2**32 if unsigned_digest >= 2**31 else unsigned_digest
    async with db.engine.connect() as conn:
        result = await conn.execute(
            text("SELECT pg_try_advisory_lock(:namespace, :digest)"),
            {"namespace": _NAMESPACE, "digest": digest},
        )
        acquired = bool(result.scalar())
        try:
            yield acquired
        finally:
            if acquired:
                await conn.execute(
                    text("SELECT pg_advisory_unlock(:namespace, :digest)"),
                    {"namespace": _NAMESPACE, "digest": digest},
                )
