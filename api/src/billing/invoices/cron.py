"""Jobs periódicos de facturación: transiciones de mora y generación mensual."""

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from billing.exchange_rates.exchange_rate_service import ExchangeRateService
from billing.gateways.resolver import PaymentGatewayResolver
from billing.invoices.repository.invoice_repository import InvoiceRepository
from billing.invoices.repository.payment_attempt_repository import (
    InvoicePaymentAttemptRepository,
)
from billing.invoices.services.billing_cron_service import BillingCronService
from billing.invoices.services.invoice_service import InvoiceService
from core.config.logger import logger
from core.database.database import db
from identity.organizations.repository.organization_repository import (
    OrganizationRepository,
)
from messaging.contacts.repository.contact_repository import ContactRepository


class _JobState:
    running = False
    monthly_running = False


_state = _JobState()


def _make_invoice_service(session: AsyncSession) -> InvoiceService:
    return InvoiceService(
        session,
        InvoiceRepository(session),
        InvoicePaymentAttemptRepository(session),
        ContactRepository(session),
        OrganizationRepository(session),
        PaymentGatewayResolver(),
    )


async def _job() -> None:
    if _state.running:
        logger.debug("[billing_cron] tick saltado: ejecucion previa en curso")
        return
    _state.running = True
    try:
        async with db.get_session() as session:
            await _make_invoice_service(session).run_overdue_transitions()
    except asyncio.CancelledError:
        logger.info("[billing_cron] transiciones canceladas (apagado en curso)")
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("[billing_cron] error en transiciones overdue/blocked")
    finally:
        _state.running = False


async def _monthly_job() -> None:
    if _state.monthly_running:
        logger.debug(
            "[billing_cron] generacion mensual saltada: ejecucion previa en curso"
        )
        return
    _state.monthly_running = True
    try:
        async with db.get_session() as session:
            billing_cron_service = BillingCronService(
                _make_invoice_service(session),
                OrganizationRepository(session),
                ExchangeRateService(),
            )
            await billing_cron_service.generate_monthly_invoices()
    except asyncio.CancelledError:
        logger.info("[billing_cron] generacion mensual cancelada (apagado en curso)")
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("[billing_cron] error en generacion mensual de facturas")
    finally:
        _state.monthly_running = False


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
