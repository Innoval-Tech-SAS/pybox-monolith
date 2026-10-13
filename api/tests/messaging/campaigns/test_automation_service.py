"""Tests del guard de concurrencia y del corte por facturación del scheduler de
campañas automáticas (ver automation_service.py). El riesgo real acá es doble: un
tick solapado que envíe el mismo lote dos veces (_executing sin liberar), o una
excepción que deje el guard bloqueado para siempre y la campaña nunca más se
procese.

Son tests unitarios puros -- construyen `AutomationService` con todas sus
dependencias mockeadas (ninguna toca la base de datos real) y parchan
`db.get_session`/`make_automation_service` a nivel de módulo, que es lo que
`_guarded_process` usa internamente sin pasar por `self`.
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.campaigns.models.campaign_time_model import CampaignTimeModel
from messaging.campaigns.services import automation_service as automation_service_module
from messaging.campaigns.services.automation_service import AutomationService


def build_service(**overrides) -> AutomationService:
    """Instancia con todas las dependencias mockeadas -- ninguno de los tests de
    este archivo necesita que hagan algo real, solo controlar sus retornos."""
    portfolio_repo = MagicMock()
    portfolio_repo.session = MagicMock()

    kwargs = dict(
        session=MagicMock(),
        campaign_repo=AsyncMock(),
        ct_repo=AsyncMock(),
        result_repo=AsyncMock(),
        channel_repo=AsyncMock(),
        seg_repo=AsyncMock(),
        dml=AsyncMock(),
        batch_sender=AsyncMock(),
        billing_status_service=AsyncMock(),
        template_var_service=AsyncMock(),
        personalization=AsyncMock(),
        contact_method_repo=AsyncMock(),
        debtor_repo=AsyncMock(),
        portfolio_repo=portfolio_repo,
        whatsapp_credentials_repo=AsyncMock(),
        whatsapp_template_data_repo=AsyncMock(),
        whatsapp_channel_request_service=AsyncMock(),
        whatsapp_client=AsyncMock(),
    )
    kwargs.update(overrides)
    return AutomationService(**kwargs)


@asynccontextmanager
async def _fake_get_session():
    yield MagicMock()


class TestGuardedProcessConcurrencyGuard:
    async def test_second_call_for_same_campaign_returns_false_without_calling_process_due(
        self,
    ):
        campaign_id = uuid.uuid4()
        ct = MagicMock(spec=CampaignTimeModel)
        ct.campaign_id = campaign_id

        first_call_started = asyncio.Event()
        release_first = asyncio.Event()

        async def slow_process_due(_ct, _now):
            first_call_started.set()
            await release_first.wait()
            return True

        mock_svc = MagicMock()
        mock_svc._ct_repo.get_by_id = AsyncMock(return_value=ct)
        mock_svc._process_due = AsyncMock(side_effect=slow_process_due)

        with (
            patch.object(
                automation_service_module.db,
                "get_session",
                side_effect=lambda: _fake_get_session(),
            ),
            patch.object(
                automation_service_module,
                "make_automation_service",
                return_value=mock_svc,
            ),
        ):
            service = build_service()

            task1 = asyncio.create_task(
                service._guarded_process(uuid.uuid4(), datetime.now(timezone.utc))
            )
            await first_call_started.wait()

            # Segunda llamada "concurrente" para la MISMA campaña, mientras la primera
            # sigue en curso (bloqueada en el evento): debe cortar por el guard, no
            # volver a invocar _process_due.
            result2 = await service._guarded_process(
                uuid.uuid4(), datetime.now(timezone.utc)
            )
            assert result2 is False

            release_first.set()
            result1 = await task1
            assert result1 is True

        # Solo la primera llamada llegó a ejecutar el envío -- la segunda se cortó en
        # el guard antes de tocar _process_due.
        assert mock_svc._process_due.call_count == 1
        assert campaign_id not in automation_service_module._executing


class TestGuardedProcessReleasesOnException:
    async def test_guard_is_released_in_finally_after_process_due_raises(self):
        campaign_id = uuid.uuid4()
        ct = MagicMock(spec=CampaignTimeModel)
        ct.campaign_id = campaign_id

        mock_svc = MagicMock()
        mock_svc._ct_repo.get_by_id = AsyncMock(return_value=ct)
        mock_svc._process_due = AsyncMock(
            side_effect=RuntimeError("fallo simulado en el envío")
        )

        with (
            patch.object(
                automation_service_module.db,
                "get_session",
                side_effect=lambda: _fake_get_session(),
            ),
            patch.object(
                automation_service_module,
                "make_automation_service",
                return_value=mock_svc,
            ),
        ):
            service = build_service()

            try:
                await service._guarded_process(uuid.uuid4(), datetime.now(timezone.utc))
                raised = False
            except RuntimeError:
                raised = True
            assert raised is True

            # El finally de _guarded_process debe haber sacado la campaña de _executing
            # a pesar de la excepción -- si no, queda bloqueada para siempre.
            assert campaign_id not in automation_service_module._executing

            # Una llamada posterior para la misma campaña ya no debe seguir bloqueada.
            mock_svc._process_due = AsyncMock(return_value=True)
            result = await service._guarded_process(
                uuid.uuid4(), datetime.now(timezone.utc)
            )
            assert result is True


class TestProcessDueBillingBlock:
    async def test_blocked_organization_skips_send_without_deactivating_schedule(self):
        campaign = MagicMock(spec=CampaignModel)
        campaign.id = uuid.uuid4()

        ct = MagicMock(spec=CampaignTimeModel)
        ct.id = uuid.uuid4()
        ct.campaign_id = campaign.id
        ct.organization_id = uuid.uuid4()

        service = build_service()
        service._campaign_repo.get_by_id = AsyncMock(return_value=campaign)
        service._billing_status_service.is_blocked = AsyncMock(return_value=True)
        service._ct_repo.deactivate = AsyncMock()
        service._ct_repo.reschedule = AsyncMock()
        service._campaign_repo.update = AsyncMock()

        result = await service._process_due(ct, datetime.now(timezone.utc))

        assert result is False
        # No se pierde el envío: se reintenta en el siguiente tick, no se desactiva
        # ni se marca la campaña como completada/fallida.
        service._ct_repo.deactivate.assert_not_called()
        service._ct_repo.reschedule.assert_not_called()
        service._campaign_repo.update.assert_not_called()
