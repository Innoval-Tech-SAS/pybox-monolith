"""Resuelve las variables de personalización de un mensaje para un deudor."""

import uuid
from typing import Any

from messaging.campaigns.constants import (
    CREDIT_TABLE,
    DEBTOR_TABLE,
    PAYMENT_STRATEGY_SUFFIXES,
    PAYMENT_TABLE,
)
from messaging.campaigns.utils.model_introspection_utils import column_attr_map
from receivables.credits.models.credit_model import CreditModel
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.debtors.models.debtor_model import DebtorModel
from receivables.debtors.repository.debtor_repository import DebtorRepository
from receivables.payments.models.payment_model import PaymentModel
from receivables.payments.repository.payment_repository import PaymentRepository

# Por estrategia de cuota, qué método del repositorio trae "el pago relevante" por
# crédito (ver PAYMENT_STRATEGY_SUFFIXES — el sufijo de la variable ya dice cuál usar).
_PAYMENT_FETCHERS: dict[str, str] = {
    "proxima_cuota": "get_next_due_by_credit_ids",
    "primera_vencida": "get_oldest_overdue_by_credit_ids",
    "ultima_sin_pagar": "get_last_unpaid_by_credit_ids",
}


class PersonalizationService:
    """
    Resuelve los valores de las variables que usa el mensaje de una
    campaña, por destinatario.

    Independiente del segmento: el segmento define la poblacion (que
    deudores matchean el filtro), esto solo trae las columnas que el
    mensaje referencia, vía los repositorios de deudores/creditos/pagos.
    """

    def __init__(
        self,
        debtor_repo: DebtorRepository,
        credit_repo: CreditRepository,
        payment_repo: PaymentRepository,
    ) -> None:
        self._debtor_repo = debtor_repo
        self._credit_repo = credit_repo
        self._payment_repo = payment_repo

    async def fetch(
        self,
        debtor_ids: list[uuid.UUID],
        fields_by_table: dict[str, set[str]],
    ) -> dict[uuid.UUID, dict[str, Any]]:
        debtor_fields = fields_by_table.get(DEBTOR_TABLE, set())
        credit_fields = fields_by_table.get(CREDIT_TABLE, set())
        payment_fields = fields_by_table.get(PAYMENT_TABLE, set())
        if not debtor_ids or not (debtor_fields or credit_fields or payment_fields):
            return {}

        data: dict[uuid.UUID, dict[str, Any]] = {}

        if debtor_fields:
            attr_by_column = column_attr_map(DebtorModel)
            for debtor in await self._debtor_repo.get_by_ids(debtor_ids):
                values = data.setdefault(debtor.id, {})
                for field in debtor_fields:
                    attr = attr_by_column.get(field)
                    if attr:
                        values[field] = getattr(debtor, attr)

        # Los pagos cuelgan del crédito, no del deudor directamente — si
        # se pidió algo de pagos, hace falta el crédito vigente igual
        # que si se hubiera pedido credit_fields.
        credits_by_debtor: dict[uuid.UUID, CreditModel] = {}
        if credit_fields or payment_fields:
            credits_by_debtor = {
                credit.debtor_id: credit
                for credit in await self._credit_repo.get_latest_by_debtor_ids(
                    debtor_ids
                )
            }

        if credit_fields:
            attr_by_column = column_attr_map(CreditModel)
            for credit in credits_by_debtor.values():
                values = data.setdefault(credit.debtor_id, {})
                for field in credit_fields:
                    attr = attr_by_column.get(field)
                    if attr:
                        values[field] = getattr(credit, attr)

        if payment_fields:
            await self._fetch_payment_fields(data, credits_by_debtor, payment_fields)

        return data

    async def _fetch_payment_fields(
        self,
        data: dict[uuid.UUID, dict[str, Any]],
        credits_by_debtor: dict[uuid.UUID, CreditModel],
        payment_fields: set[str],
    ) -> None:
        if not credits_by_debtor:
            return

        # Separa cada clave pedida (ej. "monto_pago_proxima_cuota") en la columna real
        # de `pagos` ("monto_pago") y la estrategia ("proxima_cuota"), agrupando por
        # estrategia para no repetir la consulta por cada columna que la use.
        fields_by_strategy: dict[str, set[tuple[str, str]]] = {}
        for qualified_field in payment_fields:
            for suffix in PAYMENT_STRATEGY_SUFFIXES:
                if qualified_field.endswith(f"_{suffix}"):
                    base_field = qualified_field[: -(len(suffix) + 1)]
                    fields_by_strategy.setdefault(suffix, set()).add(
                        (base_field, qualified_field)
                    )
                    break

        if not fields_by_strategy:
            return

        credit_id_to_debtor = {
            credit.id: debtor_id for debtor_id, credit in credits_by_debtor.items()
        }
        credit_ids = list(credit_id_to_debtor.keys())
        attr_by_column = column_attr_map(PaymentModel)

        for suffix, base_and_qualified in fields_by_strategy.items():
            fetcher_name = _PAYMENT_FETCHERS.get(suffix)
            if fetcher_name is None:
                continue
            payments = await getattr(self._payment_repo, fetcher_name)(credit_ids)
            for payment in payments:
                debtor_id = credit_id_to_debtor.get(payment.credit_id)
                if debtor_id is None:
                    continue
                values = data.setdefault(debtor_id, {})
                for base_field, qualified_field in base_and_qualified:
                    attr = attr_by_column.get(base_field)
                    if attr:
                        values[qualified_field] = getattr(payment, attr)
