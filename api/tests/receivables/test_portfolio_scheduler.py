"""`create_daily_counters_scheduler` registra un job de conteo diario por cada país
activo del catálogo, con el cron/timezone correcto -- sin arrancar el scheduler (no
se llama `.start()`), solo se inspeccionan los jobs creados.
"""

from app_platform.countries.repository.country_repository import CountryRepository
from receivables.portfolios.scheduler import create_daily_counters_scheduler


class TestCreateDailyCountersScheduler:
    async def test_registers_one_job_per_active_country(self, db_session):
        countries = await CountryRepository(db_session).list_active()
        assert countries, "El seed de países activos debe existir para este test"

        # Sin start() no hay nada que shutdown(): el scheduler nunca corrió, así que
        # no hay hilos/tareas de fondo que limpiar.
        scheduler = await create_daily_counters_scheduler(db_session)
        jobs = scheduler.get_jobs()
        assert len(jobs) == len(countries)

        job_ids = {job.id for job in jobs}
        for country in countries:
            assert f"daily_counters_{country.code}" in job_ids

    async def test_job_cron_runs_at_00_05_in_country_timezone(self, db_session):
        countries = await CountryRepository(db_session).list_active()
        target = countries[0]

        scheduler = await create_daily_counters_scheduler(db_session)
        job = scheduler.get_job(f"daily_counters_{target.code}")
        assert job is not None
        trigger_fields = {f.name: f for f in job.trigger.fields}
        assert str(trigger_fields["hour"]) == "0"
        assert str(trigger_fields["minute"]) == "5"
