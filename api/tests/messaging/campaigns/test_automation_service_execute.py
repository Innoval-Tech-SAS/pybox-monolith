"""Tests de `AutomationService._execute_campaign_once` (ver automation_service.py,
líneas ~239-449): la parte que resuelve el segmento, arma los destinatarios y
dispara el envío real de una campaña. Es la porción más grande y menos cubierta del
archivo -- se prueban los cortes tempranos (segmento sin datos, canal no encontrado,
sin destinatarios válidos) y un camino feliz de SMS de punta a punta contra mocks.

Reutiliza `build_service` de test_automation_service.py (mismas dependencias
mockeadas) para no duplicar la construcción del servicio.
"""

import json
import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

from messaging.campaigns.enums.campaign_enums import CampaignStatus
from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.campaigns.models.campaign_time_model import CampaignTimeModel
from messaging.campaigns.schemas.batch_schemas import BatchStats
from messaging.channels.enums.channel_enums import ChannelName, Currency
from receivables.contact_methods.enums.contact_method_enums import ContactMethodType
from tests.messaging.campaigns.test_automation_service import build_service


def make_campaign(**overrides) -> MagicMock:
    campaign = MagicMock(spec=CampaignModel)
    defaults = dict(
        id=uuid.uuid4(),
        portfolio_id=uuid.uuid4(),
        segment_id=uuid.uuid4(),
        channel_id=uuid.uuid4(),
        template_id=None,
        message="hola, tienes un saldo pendiente",
        subject=None,
        name="Campaña de prueba",
    )
    defaults.update(overrides)
    for key, value in defaults.items():
        setattr(campaign, key, value)
    return campaign


def make_ct(campaign_id: uuid.UUID, **overrides) -> MagicMock:
    ct = MagicMock(spec=CampaignTimeModel)
    defaults = dict(
        id=uuid.uuid4(), campaign_id=campaign_id, organization_id=uuid.uuid4()
    )
    defaults.update(overrides)
    for key, value in defaults.items():
        setattr(ct, key, value)
    return ct


def dml_success(rows: list[dict]) -> dict:
    return {"success": True, "data": json.dumps(rows)}


def make_channel(name: ChannelName = ChannelName.SMS) -> MagicMock:
    channel = MagicMock()
    channel.id = uuid.uuid4()
    channel.name = name
    channel.currency = Currency.COP
    channel.unit_price = 100
    return channel


class TestExecuteCampaignOnceEarlyReturns:
    async def test_no_segment_id_is_skipped_without_dml(self):
        service = build_service()
        campaign = make_campaign(segment_id=None)
        ct = make_ct(campaign.id)

        await service._execute_campaign_once(campaign, ct)

        service._dml.execute_query.assert_not_awaited()

    async def test_segment_not_found_is_skipped(self):
        service = build_service()
        campaign = make_campaign()
        ct = make_ct(campaign.id)
        service._seg_repo.get_by_id = AsyncMock(return_value=None)

        await service._execute_campaign_once(campaign, ct)

        service._dml.execute_query.assert_not_awaited()

    async def test_dml_failure_is_skipped(self):
        service = build_service()
        campaign = make_campaign()
        ct = make_ct(campaign.id)
        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=uuid.uuid4(),
            )
        )
        service._portfolio_repo.get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        service._dml.execute_query = AsyncMock(
            return_value={"success": False, "error": "boom"}
        )

        await service._execute_campaign_once(campaign, ct)

        service._channel_repo.get_by_id.assert_not_awaited()

    async def test_empty_segment_rows_is_skipped(self):
        service = build_service()
        campaign = make_campaign()
        ct = make_ct(campaign.id)
        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=uuid.uuid4(),
            )
        )
        service._portfolio_repo.get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        service._dml.execute_query = AsyncMock(return_value=dml_success([]))

        await service._execute_campaign_once(campaign, ct)

        service._channel_repo.get_by_id.assert_not_awaited()

    async def test_channel_not_found_is_skipped(self):
        service = build_service()
        campaign = make_campaign()
        ct = make_ct(campaign.id)
        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=uuid.uuid4(),
            )
        )
        service._portfolio_repo.get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        service._dml.execute_query = AsyncMock(
            return_value=dml_success([{"id": str(uuid.uuid4())}])
        )
        service._channel_repo.get_by_id = AsyncMock(return_value=None)

        await service._execute_campaign_once(campaign, ct)

        service._contact_method_repo.get_all_values_by_debtors.assert_not_awaited()

    async def test_no_debtor_ids_extracted_is_skipped(self):
        """Las filas del segmento vinieron sin un id de deudor válido (columna
        equivocada o dato corrupto) -- no debe intentar resolver contactos."""
        service = build_service()
        campaign = make_campaign()
        ct = make_ct(campaign.id)
        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=uuid.uuid4(),
            )
        )
        service._portfolio_repo.get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        service._dml.execute_query = AsyncMock(
            return_value=dml_success([{"id": "no-es-un-uuid"}])
        )
        service._channel_repo.get_by_id = AsyncMock(return_value=make_channel())

        await service._execute_campaign_once(campaign, ct)

        service._contact_method_repo.get_all_values_by_debtors.assert_not_awaited()

    async def test_whatsapp_without_active_credentials_is_skipped(self):
        service = build_service()
        campaign = make_campaign()
        ct = make_ct(campaign.id)
        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=uuid.uuid4(),
            )
        )
        service._portfolio_repo.get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        service._dml.execute_query = AsyncMock(
            return_value=dml_success([{"id": str(uuid.uuid4())}])
        )
        service._channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.WHATSAPP)
        )
        service._whatsapp_credentials_repo.get_by_organization = AsyncMock(
            return_value=None
        )

        await service._execute_campaign_once(campaign, ct)

        service._contact_method_repo.get_all_values_by_debtors.assert_not_awaited()

    async def test_whatsapp_without_template_id_is_skipped(self):
        service = build_service()
        campaign = make_campaign(template_id=None)
        ct = make_ct(campaign.id)
        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=uuid.uuid4(),
            )
        )
        service._portfolio_repo.get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        service._dml.execute_query = AsyncMock(
            return_value=dml_success([{"id": str(uuid.uuid4())}])
        )
        service._channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.WHATSAPP)
        )
        service._whatsapp_credentials_repo.get_by_organization = AsyncMock(
            return_value=MagicMock(active=True, phone_number_id="PN-1")
        )

        await service._execute_campaign_once(campaign, ct)

        service._contact_method_repo.get_all_values_by_debtors.assert_not_awaited()

    async def test_no_recipients_with_valid_contact_is_skipped_without_sending(self):
        service = build_service()
        campaign = make_campaign()
        ct = make_ct(campaign.id)
        debtor_id = uuid.uuid4()
        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=uuid.uuid4(),
            )
        )
        service._portfolio_repo.get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4(), country="CO")
        )
        service._dml.execute_query = AsyncMock(
            return_value=dml_success([{"id": str(debtor_id)}])
        )
        service._channel_repo.get_by_id = AsyncMock(return_value=make_channel())
        service._contact_method_repo.get_all_values_by_debtors = AsyncMock(
            return_value={debtor_id: []}
        )
        service._debtor_repo.get_by_ids = AsyncMock(
            return_value=[MagicMock(id=debtor_id, document_number=None)]
        )
        service._country_repo = AsyncMock()
        service._country_repo.get_phone_prefix = AsyncMock(return_value="57")

        await service._execute_campaign_once(campaign, ct)

        service._batch_sender.process_batch.assert_not_awaited()


class TestExecuteCampaignOnceSmsHappyPath:
    async def test_builds_send_inputs_and_persists_result_in_savepoint(self):
        service = build_service()
        campaign = make_campaign(message="hola sin variables")
        ct = make_ct(campaign.id)
        debtor_id = uuid.uuid4()

        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=campaign.portfolio_id,
            )
        )
        portfolio = MagicMock(organization_id=ct.organization_id, country="CO")
        service._portfolio_repo.get_by_id = AsyncMock(return_value=portfolio)
        service._dml.execute_query = AsyncMock(
            return_value=dml_success([{"id": str(debtor_id)}])
        )
        channel = make_channel(ChannelName.SMS)
        service._channel_repo.get_by_id = AsyncMock(return_value=channel)
        service._contact_method_repo.get_all_values_by_debtors = AsyncMock(
            return_value={debtor_id: ["3001234567"]}
        )
        service._debtor_repo.get_by_ids = AsyncMock(
            return_value=[MagicMock(id=debtor_id, document_number=None)]
        )
        service._template_var_service.list_available_variables = AsyncMock(
            return_value=[]
        )

        service._country_repo = AsyncMock()
        service._country_repo.get_phone_prefix = AsyncMock(return_value="57")

        stats = BatchStats(
            total_sent=1, success_count=1, failure_count=0, unique_customers=1
        )
        service._batch_sender.process_batch = AsyncMock(return_value=stats)

        @asynccontextmanager
        async def _nested():
            yield

        service._session.begin_nested = MagicMock(return_value=_nested())
        service._result_repo.create = AsyncMock()

        await service._execute_campaign_once(campaign, ct)

        service._batch_sender.process_batch.assert_awaited_once()
        call = service._batch_sender.process_batch.await_args
        send_inputs = call.args[0]
        assert len(send_inputs) == 1
        # La normalización con indicativo ocurre dentro de BatchSender._send_chunk,
        # justo antes de enviar -- acá el recipient todavía va crudo, pero el
        # phone_prefix resuelto viaja como kwarg para que esa capa lo aplique.
        assert send_inputs[0].recipient == "3001234567"
        assert call.kwargs["phone_prefix"] == "57"
        assert send_inputs[0].campaign_id == campaign.id
        assert call.args[1] == ChannelName.SMS

        service._result_repo.create.assert_awaited_once_with(
            campaign_id=campaign.id,
            organization_id=ct.organization_id,
            campaign_time_id=ct.id,
            total_sent=1,
            success_count=1,
            failure_count=0,
            unique_customers=1,
        )

    async def test_result_registration_failure_does_not_propagate(self):
        """El registro del resultado va en un savepoint aislado (ver comentario en
        automation_service.py): si falla, no debe tumbar el resto del procesamiento
        de la campaña (la reprogramación posterior en _process_due debe poder seguir).
        """
        service = build_service()
        campaign = make_campaign(message="hola sin variables")
        ct = make_ct(campaign.id)
        debtor_id = uuid.uuid4()

        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=campaign.portfolio_id,
            )
        )
        service._portfolio_repo.get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=ct.organization_id, country="CO")
        )
        service._dml.execute_query = AsyncMock(
            return_value=dml_success([{"id": str(debtor_id)}])
        )
        service._channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.SMS)
        )
        service._contact_method_repo.get_all_values_by_debtors = AsyncMock(
            return_value={debtor_id: ["3001234567"]}
        )
        service._debtor_repo.get_by_ids = AsyncMock(
            return_value=[MagicMock(id=debtor_id, document_number=None)]
        )
        service._template_var_service.list_available_variables = AsyncMock(
            return_value=[]
        )
        service._country_repo = AsyncMock()
        service._country_repo.get_phone_prefix = AsyncMock(return_value="57")
        service._batch_sender.process_batch = AsyncMock(
            return_value=BatchStats(
                total_sent=1, success_count=1, failure_count=0, unique_customers=1
            )
        )

        @asynccontextmanager
        async def _nested():
            yield
            raise RuntimeError("fallo insertando el resultado")

        service._session.begin_nested = MagicMock(return_value=_nested())

        # No debe lanzar -- el except Exception alrededor del begin_nested se traga el error.
        await service._execute_campaign_once(campaign, ct)


class TestExecuteCampaignOnceWhatsAppConsent:
    """Fase 6 de la auditoría: los teléfonos SIN caso previo (no cubiertos por el
    prefetch de `get_existing_statuses`) se crean todos de una vez vía
    `ensure_cases_bulk`, en vez de un `ensure_case` por destinatario dentro del loop.
    Cubre el caso mixto: un teléfono ya aprobado (prefetch) + uno nuevo (bulk-creado,
    queda PENDIENTE y por lo tanto excluido de los destinatarios de este envío)."""

    async def test_missing_phone_is_bulk_created_and_excluded_as_pending(self):
        from messaging.whatsapp.enums.whatsapp_enums import ChannelRequestStatus

        service = build_service()
        campaign = make_campaign(template_id=uuid.uuid4())
        ct = make_ct(campaign.id)
        debtor_approved = uuid.uuid4()
        debtor_pending = uuid.uuid4()

        service._seg_repo.get_by_id = AsyncMock(
            return_value=MagicMock(
                filter_criteria={"tables": [{"name": "deudores"}]},
                portfolio_id=campaign.portfolio_id,
            )
        )
        service._portfolio_repo.get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=ct.organization_id, country="CO")
        )
        service._dml.execute_query = AsyncMock(
            return_value=dml_success(
                [{"id": str(debtor_approved)}, {"id": str(debtor_pending)}]
            )
        )
        service._channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.WHATSAPP)
        )
        service._whatsapp_credentials_repo.get_by_organization = AsyncMock(
            return_value=MagicMock(active=True, phone_number_id="PN-1")
        )
        service._whatsapp_template_data_repo.get_by_template_id = AsyncMock(
            return_value=MagicMock(
                meta_name="plantilla_saldo", language="es", meta_template_id=None
            )
        )
        service._contact_method_repo.get_all_values_by_debtors = AsyncMock(
            return_value={
                debtor_approved: ["3001111111"],
                debtor_pending: ["3002222222"],
            }
        )
        service._debtor_repo.get_by_ids = AsyncMock(
            return_value=[
                MagicMock(id=debtor_approved, document_number=None),
                MagicMock(id=debtor_pending, document_number=None),
            ]
        )
        service._template_var_service.list_available_variables = AsyncMock(
            return_value=[]
        )
        service._country_repo = AsyncMock()
        service._country_repo.get_phone_prefix = AsyncMock(return_value="57")

        # Prefetch: solo el teléfono del debtor_approved tiene caso previo (APROBADA).
        service._whatsapp_channel_request_service.get_existing_statuses = AsyncMock(
            return_value={"573001111111": ChannelRequestStatus.APPROVED}
        )
        service._whatsapp_channel_request_service.ensure_cases_bulk = AsyncMock()

        stats = BatchStats(
            total_sent=1, success_count=1, failure_count=0, unique_customers=1
        )
        service._batch_sender.process_batch = AsyncMock(return_value=stats)

        @asynccontextmanager
        async def _nested():
            yield

        service._session.begin_nested = MagicMock(return_value=_nested())
        service._result_repo.create = AsyncMock()

        await service._execute_campaign_once(campaign, ct)

        # El teléfono sin caso previo se creó en bulk (no via ensure_case por fila).
        service._whatsapp_channel_request_service.ensure_cases_bulk.assert_awaited_once()
        bulk_call = (
            service._whatsapp_channel_request_service.ensure_cases_bulk.await_args
        )
        assert bulk_call.args[0] == ct.organization_id
        assert bulk_call.args[1] == {"573002222222": debtor_pending}
        assert bulk_call.kwargs["origin_campaign_id"] == campaign.id

        # Solo el teléfono ya aprobado (prefetch) entra al envío; el recién creado
        # queda PENDIENTE y se excluye, igual que hacía ensure_case fila por fila.
        service._batch_sender.process_batch.assert_awaited_once()
        send_inputs = service._batch_sender.process_batch.await_args.args[0]
        assert len(send_inputs) == 1
        assert send_inputs[0].recipient == "3001111111"
