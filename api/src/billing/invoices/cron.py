from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.logger import logger
from core.database.database import db
from billing.invoices.monthly_billing import generate_monthly_invoices
from billing.invoices.repository.invoice_repository import InvoiceRepository
from billing.invoices.repository.payment_attempt_repository import PaymentAttemptRepository
from billing.invoices.services.invoice_service import InvoiceService
from identity.organizations.repository.organization_repository import OrganizationRepository
from messaging.contacts.repositories.contact_repository import ContactRepository

_running = False
_monthly_running = False


def _make_invoice_service(session: AsyncSession) -> InvoiceService:
    return InvoiceService(
        session, InvoiceRepository(session), PaymentAttemptRepository(session), ContactRepository(session)
    )


async def _job() -> None:
    global _running
    if _running:
        logger.debug("[billing_cron] tick saltado: ejecucion previa en curso")
        return
    _running = True
    try:
        async with db.get_session() as session:
            await _make_invoice_service(session).run_overdue_transitions()
    except Exception:
        logger.exception("[billing_cron] error en transiciones overdue/blocked")
    finally:
        _running = False


async def _monthly_job() -> None:
    global _monthly_running
    if _monthly_running:
        logger.debug("[billing_cron] generacion mensual saltada: ejecucion previa en curso")
        return
    _monthly_running = True
    try:
        async with db.get_session() as session:
            await generate_monthly_invoices(_make_invoice_service(session), OrganizationRepository(session))
    except Exception:
        logger.exception("[billing_cron] error en generacion mensual de facturas")
    finally:
        _monthly_running = False


def create_billing_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _job,
        CronTrigger(hour=2, minute=0, timezone="America/Bogota"),
        id="billing_overdue_transitions",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )
    scheduler.add_job(
        _monthly_job,
        CronTrigger(day=1, hour=3, minute=0, timezone="America/Bogota"),
        id="billing_monthly_invoices",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=600,
    )
    return scheduler
