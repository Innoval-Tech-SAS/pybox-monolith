from core.database.advisory_lock import try_advisory_lock


class TestAdvisoryLock:
    """Coordina jobs recurrentes entre los N workers de uvicorn (ver comentario en
    advisory_lock.py). Sin esto, campaigns_automation/results_reconciliation/
    daily_counters corren duplicados una vez por worker en cada tick."""

    async def test_acquires_when_free(self):
        async with try_advisory_lock("test:advisory_lock:acquire") as acquired:
            assert acquired is True

    async def test_second_holder_is_rejected_while_first_holds(self):
        async with try_advisory_lock("test:advisory_lock:contend") as first:
            assert first is True
            async with try_advisory_lock("test:advisory_lock:contend") as second:
                assert second is False

    async def test_released_after_context_exits(self):
        async with try_advisory_lock("test:advisory_lock:release") as first:
            assert first is True
        async with try_advisory_lock("test:advisory_lock:release") as second:
            assert second is True

    async def test_different_keys_do_not_contend(self):
        async with try_advisory_lock("test:advisory_lock:key_a") as a:
            async with try_advisory_lock("test:advisory_lock:key_b") as b:
                assert a is True
                assert b is True

    async def test_unsigned_crc32_overflow_does_not_crash(self):
        # zlib.crc32 devuelve un entero SIN signo de 32 bits (hasta 4294967295), pero
        # pg_try_advisory_lock(int, int) espera enteros CON signo -- esta key en
        # particular produce un CRC32 que excede 2**31-1 y antes tumbaba el arranque
        # con "value out of int32 range" (ver advisory_lock.py).
        async with try_advisory_lock("daily_counters:VE") as acquired:
            assert acquired is True
