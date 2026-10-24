"""Tests unitarios de `PersonalizationService.fetch` (ver personalization_service.py):
resuelve valores reales de deudor/crédito/pago para las variables `{{var}}` de una
campaña. Repos mockeados con AsyncMock/MagicMock -- no toca la base de datos.

El riesgo real: una variable pedida que no mapea a ninguna columna real (dato nulo o
mal escrito) no debe reventar, solo omitirse; y las variables de pago por estrategia
(proxima_cuota/primera_vencida/ultima_sin_pagar) deben resolverse contra el fetcher
correcto sin duplicar consultas por columna.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

from messaging.campaigns.services.personalization_service import PersonalizationService


def make_service():
    debtor_repo = AsyncMock()
    credit_repo = AsyncMock()
    payment_repo = AsyncMock()
    service = PersonalizationService(debtor_repo, credit_repo, payment_repo)
    return service, debtor_repo, credit_repo, payment_repo


def make_debtor(debtor_id: uuid.UUID, full_name: str = "Ana Pérez") -> MagicMock:
    debtor = MagicMock()
    debtor.id = debtor_id
    debtor.full_name = full_name
    return debtor


def make_credit(
    debtor_id: uuid.UUID,
    credit_id: uuid.UUID | None = None,
    overdue_principal_balance=250000,
) -> MagicMock:
    credit = MagicMock()
    credit.id = credit_id or uuid.uuid4()
    credit.debtor_id = debtor_id
    credit.overdue_principal_balance = overdue_principal_balance
    return credit


def make_payment(credit_id: uuid.UUID, payment_amount=50000) -> MagicMock:
    payment = MagicMock()
    payment.credit_id = credit_id
    payment.payment_amount = payment_amount
    return payment


class TestFetchNoOp:
    async def test_no_debtor_ids_returns_empty_without_calling_repos(self):
        service, debtor_repo, credit_repo, payment_repo = make_service()

        result = await service.fetch([], {"deudores": {"nombre_completo"}})

        assert result == {}
        debtor_repo.get_by_ids.assert_not_awaited()

    async def test_no_fields_requested_returns_empty_without_calling_repos(self):
        service, debtor_repo, credit_repo, payment_repo = make_service()

        result = await service.fetch([uuid.uuid4()], {})

        assert result == {}
        debtor_repo.get_by_ids.assert_not_awaited()
        credit_repo.get_latest_by_debtor_ids.assert_not_awaited()


class TestFetchDebtorFields:
    async def test_resolves_debtor_column_to_real_value(self):
        service, debtor_repo, credit_repo, payment_repo = make_service()
        debtor_id = uuid.uuid4()
        debtor_repo.get_by_ids = AsyncMock(
            return_value=[make_debtor(debtor_id, "Ana Pérez")]
        )

        result = await service.fetch([debtor_id], {"deudores": {"nombre_completo"}})

        assert result == {debtor_id: {"nombre_completo": "Ana Pérez"}}
        credit_repo.get_latest_by_debtor_ids.assert_not_awaited()

    async def test_unknown_column_name_is_silently_skipped(self):
        """Una variable con una columna que no existe en el modelo (typo, o columna
        renombrada) no debe reventar -- simplemente no aporta valor."""
        service, debtor_repo, credit_repo, payment_repo = make_service()
        debtor_id = uuid.uuid4()
        debtor_repo.get_by_ids = AsyncMock(return_value=[make_debtor(debtor_id)])

        result = await service.fetch([debtor_id], {"deudores": {"columna_inexistente"}})

        assert result == {debtor_id: {}}


class TestFetchCreditFields:
    async def test_resolves_credit_column_via_latest_credit(self):
        service, debtor_repo, credit_repo, payment_repo = make_service()
        debtor_id = uuid.uuid4()
        credit_repo.get_latest_by_debtor_ids = AsyncMock(
            return_value=[make_credit(debtor_id, overdue_principal_balance=125000)]
        )

        result = await service.fetch([debtor_id], {"creditos": {"saldo_capital_mora"}})

        assert result == {debtor_id: {"saldo_capital_mora": 125000}}
        debtor_repo.get_by_ids.assert_not_awaited()


class TestFetchPaymentFields:
    async def test_resolves_payment_field_using_correct_strategy_fetcher(self):
        service, debtor_repo, credit_repo, payment_repo = make_service()
        debtor_id = uuid.uuid4()
        credit = make_credit(debtor_id)
        credit_repo.get_latest_by_debtor_ids = AsyncMock(return_value=[credit])
        payment_repo.get_next_due_by_credit_ids = AsyncMock(
            return_value=[make_payment(credit.id, payment_amount=99000)]
        )

        result = await service.fetch(
            [debtor_id], {"pagos": {"monto_pago_proxima_cuota"}}
        )

        assert result == {debtor_id: {"monto_pago_proxima_cuota": 99000}}
        payment_repo.get_next_due_by_credit_ids.assert_awaited_once_with([credit.id])
        payment_repo.get_oldest_overdue_by_credit_ids.assert_not_called()

    async def test_multiple_fields_same_strategy_only_calls_fetcher_once(self):
        """monto_pago_primera_vencida y fecha_pago_primera_vencida comparten estrategia
        (primera_vencida) -- deben agruparse en una sola consulta, no una por columna.
        """
        service, debtor_repo, credit_repo, payment_repo = make_service()
        debtor_id = uuid.uuid4()
        credit = make_credit(debtor_id)
        credit_repo.get_latest_by_debtor_ids = AsyncMock(return_value=[credit])
        payment = make_payment(credit.id, payment_amount=30000)
        payment.payment_date = "2026-08-01"
        payment_repo.get_oldest_overdue_by_credit_ids = AsyncMock(
            return_value=[payment]
        )

        result = await service.fetch(
            [debtor_id],
            {"pagos": {"monto_pago_primera_vencida", "fecha_pago_primera_vencida"}},
        )

        assert result[debtor_id]["monto_pago_primera_vencida"] == 30000
        assert result[debtor_id]["fecha_pago_primera_vencida"] == "2026-08-01"
        assert payment_repo.get_oldest_overdue_by_credit_ids.call_count == 1

    async def test_debtor_without_credit_has_no_payment_data(self):
        """Si un deudor no tiene crédito vigente, sus pagos no se pueden resolver --
        no debe aparecer en el resultado ni reventar el fetch de otros deudores."""
        service, debtor_repo, credit_repo, payment_repo = make_service()
        debtor_with_credit = uuid.uuid4()
        debtor_without_credit = uuid.uuid4()
        credit = make_credit(debtor_with_credit)
        credit_repo.get_latest_by_debtor_ids = AsyncMock(return_value=[credit])
        payment_repo.get_next_due_by_credit_ids = AsyncMock(
            return_value=[make_payment(credit.id, payment_amount=1000)]
        )

        result = await service.fetch(
            [debtor_with_credit, debtor_without_credit],
            {"pagos": {"monto_pago_proxima_cuota"}},
        )

        assert debtor_with_credit in result
        assert debtor_without_credit not in result

    async def test_no_credits_at_all_short_circuits_without_calling_payment_repo(self):
        service, debtor_repo, credit_repo, payment_repo = make_service()
        debtor_id = uuid.uuid4()
        credit_repo.get_latest_by_debtor_ids = AsyncMock(return_value=[])

        result = await service.fetch(
            [debtor_id], {"pagos": {"monto_pago_proxima_cuota"}}
        )

        assert result == {}
        payment_repo.get_next_due_by_credit_ids.assert_not_called()

    async def test_field_without_known_strategy_suffix_is_ignored(self):
        service, debtor_repo, credit_repo, payment_repo = make_service()
        debtor_id = uuid.uuid4()
        credit_repo.get_latest_by_debtor_ids = AsyncMock(
            return_value=[make_credit(debtor_id)]
        )

        result = await service.fetch(
            [debtor_id], {"pagos": {"monto_pago_sin_sufijo_valido"}}
        )

        assert result == {}
        payment_repo.get_next_due_by_credit_ids.assert_not_called()


class TestFetchCombinedTables:
    async def test_combines_debtor_credit_and_payment_fields_for_same_debtor(self):
        service, debtor_repo, credit_repo, payment_repo = make_service()
        debtor_id = uuid.uuid4()
        debtor_repo.get_by_ids = AsyncMock(
            return_value=[make_debtor(debtor_id, "Carlos Ruiz")]
        )
        credit = make_credit(debtor_id, overdue_principal_balance=75000)
        credit_repo.get_latest_by_debtor_ids = AsyncMock(return_value=[credit])
        payment_repo.get_last_unpaid_by_credit_ids = AsyncMock(
            return_value=[make_payment(credit.id, payment_amount=5000)]
        )

        result = await service.fetch(
            [debtor_id],
            {
                "deudores": {"nombre_completo"},
                "creditos": {"saldo_capital_mora"},
                "pagos": {"monto_pago_ultima_sin_pagar"},
            },
        )

        assert result == {
            debtor_id: {
                "nombre_completo": "Carlos Ruiz",
                "saldo_capital_mora": 75000,
                "monto_pago_ultima_sin_pagar": 5000,
            }
        }
