"""Tests del wrapper del scheduler de campañas (ver cron.py): coordina el tick entre
los N workers de uvicorn vía `try_advisory_lock` y evita que ticks se solapen dentro
del mismo worker (`_running`). Unitarios puros: `try_advisory_lock`, `db.get_session`
y `make_automation_service` van parchados a nivel de módulo -- nunca toca Postgres
ni arma un `AsyncIOScheduler` real corriendo.
"""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import messaging.campaigns.cron as cron_module
from messaging.campaigns.cron import create_campaigns_scheduler


@asynccontextmanager
async def _fake_session():
    yield MagicMock()


def _lock(acquired: bool):
    @asynccontextmanager
    async def _fake_lock(_key: str):
        yield acquired

    return _fake_lock


class TestJobAdvisoryLock:
    async def test_other_worker_holding_lock_skips_processing(self):
        """Otro worker ya tiene el advisory lock (acquired=False): este tick NO debe
        tocar `make_automation_service` ni la sesión de DB -- es justo lo que el lock
        coordina entre los workers de uvicorn (ver docstring de try_advisory_lock)."""
        make_svc = MagicMock()
        with (
            patch.object(cron_module, "try_advisory_lock", side_effect=_lock(False)),
            patch.object(cron_module, "make_automation_service", make_svc),
        ):
            cron_module._running = False
            await cron_module._job()

        make_svc.assert_not_called()
        assert cron_module._running is False  # se liberó en el finally

    async def test_lock_acquired_runs_tick_and_releases_running_flag(self):
        automation_service = AsyncMock()
        automation_service.tick = AsyncMock(return_value=3)
        make_svc = MagicMock(return_value=automation_service)

        with (
            patch.object(cron_module, "try_advisory_lock", side_effect=_lock(True)),
            patch.object(cron_module, "make_automation_service", make_svc),
            patch.object(
                cron_module.db, "get_session", side_effect=lambda: _fake_session()
            ),
        ):
            cron_module._running = False
            await cron_module._job()

        automation_service.tick.assert_awaited_once()
        assert cron_module._running is False


class TestJobConcurrencyGuardWithinWorker:
    async def test_tick_already_running_in_this_worker_is_skipped(self):
        """`_running=True` (un tick anterior sigue en curso en este mismo proceso): el
        nuevo tick se corta ANTES de intentar el advisory lock."""
        lock_fn = MagicMock(side_effect=_lock(True))
        with patch.object(cron_module, "try_advisory_lock", lock_fn):
            cron_module._running = True
            try:
                await cron_module._job()
            finally:
                cron_module._running = False

        lock_fn.assert_not_called()

    async def test_running_flag_is_released_even_if_tick_raises(self):
        automation_service = AsyncMock()
        automation_service.tick = AsyncMock(
            side_effect=RuntimeError("fallo en el tick")
        )
        make_svc = MagicMock(return_value=automation_service)

        with (
            patch.object(cron_module, "try_advisory_lock", side_effect=_lock(True)),
            patch.object(cron_module, "make_automation_service", make_svc),
            patch.object(
                cron_module.db, "get_session", side_effect=lambda: _fake_session()
            ),
        ):
            cron_module._running = False
            await cron_module._job()  # no debe propagar: se loguea y se traga

        assert cron_module._running is False


class TestCreateCampaignsScheduler:
    def test_registers_a_single_job_with_max_one_instance(self):
        # No se llama start()/shutdown(): un scheduler nunca iniciado no reserva hilos
        # ni loop propio (shutdown() sin start() previo revienta con
        # SchedulerNotRunningError) -- solo se inspecciona el job registrado.
        scheduler = create_campaigns_scheduler()
        jobs = scheduler.get_jobs()
        assert len(jobs) == 1
        job = jobs[0]
        assert job.id == "campaigns_automation"
        assert job.max_instances == 1
        assert job.coalesce is True
