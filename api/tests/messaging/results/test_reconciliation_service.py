"""Tests de la reconciliación de resultados de envío contra el reporte CSV del
proveedor (ver reconciliation_service.py). El riesgo real: un `sending_id` que el
proveedor reporta pero que no quedó en BD no debe tumbar el job (IndexError sobre
listas vacías), eventos duplicados/desordenados del mismo destinatario deben
resolverse por el más reciente (no por orden de aparición en el CSV), un status
que no cambió no debe generar un UPDATE ni un CampaignResult de más, y un CSV
vacío no debe tocar la base de datos.

Unitarios puros: `ContactRepository`/`CampaignResultRepository`/proveedores van
mockeados -- solo se prueba la lógica de `ReconciliationService`, sin DB real.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

from messaging.channels.enums.channel_enums import ChannelName
from messaging.contacts.enums.contact_enums import ContactStatus
from messaging.contacts.models.contact_model import ContactModel
from messaging.results.services.reconciliation_service import ReconciliationService


def build_service(*, sms_report_csv: str, contacts: list[ContactModel]) -> tuple[ReconciliationService, MagicMock, MagicMock]:
    sms_provider = MagicMock()
    sms_provider.get_sending_events_report = AsyncMock(return_value=sms_report_csv)

    contact_repo = MagicMock()
    contact_repo.get_by_sending_id = AsyncMock(return_value=contacts)
    contact_repo.session = MagicMock()
    contact_repo.session.flush = AsyncMock()

    result_repo = MagicMock()
    result_repo.create = AsyncMock()

    service = ReconciliationService(
        contact_repo=contact_repo,
        result_repo=result_repo,
        sms_provider=sms_provider,
        email_provider=MagicMock(),
    )
    return service, contact_repo, result_repo


def make_contact(**overrides) -> ContactModel:
    contact = ContactModel(
        content="hola",
        recipient=overrides.pop("recipient", "+573001112233"),
        status=overrides.pop("status", ContactStatus.SENT),
        campaign_id=overrides.pop("campaign_id", uuid.uuid4()),
        organization_id=overrides.pop("organization_id", uuid.uuid4()),
    )
    for key, value in overrides.items():
        setattr(contact, key, value)
    return contact


class TestReconcileUnknownSendingId:
    async def test_sending_id_not_in_db_does_not_raise_or_create_result(self):
        # El reporte real de 360nrs trae ambas columnas (phone/email) sin importar el
        # canal -- `_last_event_per_recipient` las coalesce. "phone" va primero en el
        # coalesce y siempre está poblado acá, así que el valor de "email" es
        # irrelevante para el resultado; se rellena con un valor no vacío para no
        # depender de cómo infiere polars el dtype de una columna 100% vacía.
        csv_text = (
            "phone,email,event,createdAt\n"
            "+573001112233,irrelevante@example.com,DELIVERED,2026-08-19T10:00:00Z\n"
        )
        # get_by_sending_id vacío: el proveedor conoce el sending_id pero en BD no
        # quedó ningún contacto asociado (p. ej. limpieza, o nunca se completó el envío).
        service, contact_repo, result_repo = build_service(sms_report_csv=csv_text, contacts=[])

        reconciled = await service._reconcile_sending("sending-desconocido", ChannelName.SMS)

        assert reconciled is False
        result_repo.create.assert_not_called()
        contact_repo.session.flush.assert_not_called()


class TestReconcileAppliesLatestEventPerRecipient:
    async def test_out_of_order_duplicate_events_use_the_most_recent_by_date(self):
        recipient = "+573001112233"
        # 3 eventos del MISMO destinatario, deliberadamente fuera de orden cronológico
        # en el CSV -- el más reciente (15:00, HARD_BOUNCED) debe ganar, no el primero
        # en aparecer (DELIVERED) ni el más viejo (SOFT_BOUNCED).
        csv_text = (
            "phone,email,event,createdAt\n"
            f"{recipient},irrelevante@example.com,DELIVERED,2026-08-19T12:00:00Z\n"
            f"{recipient},irrelevante@example.com,SOFT_BOUNCED,2026-08-19T08:00:00Z\n"
            f"{recipient},irrelevante@example.com,HARD_BOUNCED,2026-08-19T15:00:00Z\n"
        )
        contact = make_contact(recipient=recipient, status=ContactStatus.SENT)
        service, contact_repo, result_repo = build_service(sms_report_csv=csv_text, contacts=[contact])

        reconciled = await service._reconcile_sending("sending-1", ChannelName.SMS)

        assert reconciled is True
        assert contact.status == ContactStatus.HARD_BOUNCED
        contact_repo.session.flush.assert_awaited_once()
        result_repo.create.assert_awaited_once()


class TestReconcileNoOpWhenStatusUnchanged:
    async def test_same_status_already_applied_does_not_update_or_create_result(self):
        recipient = "+573001112233"
        csv_text = (
            f"phone,email,event,createdAt\n{recipient},irrelevante@example.com,DELIVERED,2026-08-19T12:00:00Z\n"
        )
        # El contacto YA está en DELIVERED -- el proveedor reporta lo mismo que ya
        # tenemos, no hay nada que cambiar.
        contact = make_contact(recipient=recipient, status=ContactStatus.DELIVERED)
        service, contact_repo, result_repo = build_service(sms_report_csv=csv_text, contacts=[contact])

        reconciled = await service._reconcile_sending("sending-1", ChannelName.SMS)

        assert reconciled is False
        contact_repo.session.flush.assert_not_called()
        result_repo.create.assert_not_called()


class TestReconcileEmptyCsv:
    async def test_blank_csv_returns_without_touching_db(self):
        contact_repo_get_called = AsyncMock()
        service, contact_repo, result_repo = build_service(sms_report_csv="", contacts=[])
        contact_repo.get_by_sending_id = contact_repo_get_called

        reconciled = await service._reconcile_sending("sending-1", ChannelName.SMS)

        assert reconciled is False
        contact_repo_get_called.assert_not_called()
        result_repo.create.assert_not_called()

    async def test_headers_only_csv_returns_without_crashing(self):
        contact_repo_get_called = AsyncMock()
        service, contact_repo, result_repo = build_service(
            sms_report_csv="phone,event,createdAt\n", contacts=[]
        )
        contact_repo.get_by_sending_id = contact_repo_get_called

        reconciled = await service._reconcile_sending("sending-1", ChannelName.SMS)

        assert reconciled is False
        contact_repo_get_called.assert_not_called()
        result_repo.create.assert_not_called()
