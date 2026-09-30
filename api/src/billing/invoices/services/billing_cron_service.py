"""Generación mensual de facturas y transiciones de mora, orquestadas por el cron."""

from datetime import datetime, timezone
from decimal import Decimal

from app_platform.countries.repository.country_repository import CountryRepository
from billing.exchange_rates.exchange_rate_service import ExchangeRateService
from billing.invoices.schemas.invoice_params_schemas import CreateInvoiceParams
from billing.invoices.services.invoice_service import InvoiceService
from billing.invoices.utils.invoice_utils import period_bounds, previous_period
from core.config.logger import logger
from identity.organizations.repository.organization_repository import (
    OrganizationRepository,
)


class BillingCronService:
    def __init__(
        self,
        invoice_service: InvoiceService,
        organization_repo: OrganizationRepository,
        exchange_rate_service: ExchangeRateService,
    ):
        self._invoice_service = invoice_service
        self._organization_repo = organization_repo
        self._exchange_rate_service = exchange_rate_service
        self._country_repo = CountryRepository(organization_repo.session)

    async def generate_monthly_invoices(self) -> None:
        """
        Genera la factura del mes anterior para cada organizacion activa, a partir
        de su consumo real registrado en messaging.contacts. Equivalente a
        BillingCronService.generateMonthlyInvoices del legacy, salvo que el uso ya
        no se consulta a otro microservicio: se calcula directamente en este monolito.

        Cada organizacion se factura en la moneda de su pais (leida de la tabla paises,
        "COP" si no tiene pais asignado); la tasa de cambio se cachea por moneda dentro
        del loop para no consultar la API de cambio una vez por organizacion.
        """
        now = datetime.now(timezone.utc)
        period_year, period_month = previous_period(now)
        period_start, period_end = period_bounds(period_year, period_month)

        organizations = await self._organization_repo.get_all()
        logger.info(
            "[billing_monthly] procesando %d organizaciones activas", len(organizations)
        )

        country_map = await self._country_repo.get_active_map()
        exchange_rate_by_currency: dict[str, Decimal] = {}
        created = skipped = errors = 0
        for org in organizations:
            try:
                country = country_map.get(org.country) if org.country else None
                billing_currency = country.currency_code if country else "COP"
                if billing_currency not in exchange_rate_by_currency:
                    rate = await self._exchange_rate_service.get_usd_rate(
                        billing_currency
                    )
                    exchange_rate_by_currency[billing_currency] = rate
                    logger.info(
                        "[billing_monthly] tasa USD->%s: %s", billing_currency, rate
                    )
                exchange_rate = exchange_rate_by_currency[billing_currency]

                items = await self._invoice_service.build_period_items(
                    org.id, period_start, period_end
                )
                result = await self._invoice_service.create_or_skip(
                    CreateInvoiceParams(
                        organization_id=org.id,
                        period_year=period_year,
                        period_month=period_month,
                        exchange_rate=exchange_rate,
                        billing_currency=billing_currency,
                        items=items,
                    )
                )
                if result is not None:
                    created += 1
                else:
                    skipped += 1
            except Exception:
                logger.exception(
                    "[billing_monthly] error generando factura para organizacion=%s",
                    org.id,
                )
                errors += 1

        logger.info(
            "[billing_monthly] terminado | creadas=%d omitidas=%d errores=%d",
            created,
            skipped,
            errors,
        )
