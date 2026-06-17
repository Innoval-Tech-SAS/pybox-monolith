from datetime import datetime, timezone

from core.config.logger import logger
from billing.invoices.services.invoice_service import CreateInvoiceParams, InvoiceService
from billing.trm.trm_service import get_current_trm
from identity.organizations.repository.organization_repository import OrganizationRepository


def _previous_period(now: datetime) -> tuple[int, int]:
    if now.month == 1:
        return now.year - 1, 12
    return now.year, now.month - 1


def _period_bounds(period_year: int, period_month: int) -> tuple[datetime, datetime]:
    start = datetime(period_year, period_month, 1, tzinfo=timezone.utc)
    if period_month == 12:
        end = datetime(period_year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(period_year, period_month + 1, 1, tzinfo=timezone.utc)
    return start, end


async def generate_monthly_invoices(
    invoice_service: InvoiceService, organization_repo: OrganizationRepository
) -> None:
    """
    Genera la factura del mes anterior para cada organizacion activa, a partir
    de su consumo real registrado en messaging.contacts. Equivalente a
    BillingCronService.generateMonthlyInvoices del legacy, salvo que el uso ya
    no se consulta a otro microservicio: se calcula directamente en este monolito.
    """
    now = datetime.now(timezone.utc)
    period_year, period_month = _previous_period(now)
    period_start, period_end = _period_bounds(period_year, period_month)

    exchange_rate = await get_current_trm()
    logger.info("[billing_monthly] TRM para %s-%02d: %s", period_year, period_month, exchange_rate)

    organizations = await organization_repo.get_all()
    logger.info("[billing_monthly] procesando %d organizaciones activas", len(organizations))

    created = skipped = errors = 0
    for org in organizations:
        try:
            items = await invoice_service.build_period_items(org.id, period_start, period_end)
            result = await invoice_service.create_or_skip(
                CreateInvoiceParams(
                    organization_id=org.id,
                    period_year=period_year,
                    period_month=period_month,
                    exchange_rate=exchange_rate,
                    items=items,
                )
            )
            if result is not None:
                created += 1
            else:
                skipped += 1
        except Exception:
            logger.exception("[billing_monthly] error generando factura para organizacion=%s", org.id)
            errors += 1

    logger.info(
        "[billing_monthly] terminado | creadas=%d omitidas=%d errores=%d", created, skipped, errors
    )
