"""Tests unitarios de WhatsAppTemplateService (ver whatsapp_template_service.py).

Repos y cliente Meta mockeados. Cubre el armado del `meta_name` (slug + prefijo de
portafolio), el mapeo de `meta_status` -> `TemplateStatus` en `refresh_status`, y
que `list_variables`/`refresh_status` toleren una plantilla sin `meta_template_id`
(creada pero nunca sincronizada con Meta) sin llamar al cliente.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import HTTPException

from identity.users.enums.user_enums import UserRole, UserScope
from messaging.templates.enums.template_enums import TemplateChannel, TemplateStatus
from messaging.templates.models.template_model import TemplateModel
from messaging.whatsapp.enums.whatsapp_enums import WhatsAppTemplateCategory
from messaging.whatsapp.models.whatsapp_template_data_model import (
    WhatsAppTemplateDataModel,
)
from messaging.whatsapp.schemas.whatsapp_template_data_schemas import (
    WhatsAppTemplateCreateRequest,
)
from messaging.whatsapp.services.whatsapp_template_service import (
    WhatsAppTemplateService,
    _meta_name,
)
from tests.conftest import make_user_session


def build_service(**overrides) -> tuple[WhatsAppTemplateService, dict]:
    mocks = dict(
        template_repo=MagicMock(),
        data_repo=MagicMock(),
        portfolio_repo=MagicMock(),
        client=MagicMock(),
    )
    mocks.update(overrides)
    return WhatsAppTemplateService(**mocks), mocks


ADMIN_SESSION = make_user_session(role=UserRole.ADMIN, scope=UserScope.GLOBAL)


class TestMetaName:
    def test_slugifies_and_prefixes_with_portfolio_short_id(self):
        portfolio_id = uuid.UUID("12345678-aaaa-bbbb-cccc-000000000000")
        result = _meta_name(portfolio_id, "Recordatorio de Pago!!")
        assert result == "12345678_recordatorio_de_pago"

    def test_accented_and_special_characters_are_stripped(self):
        portfolio_id = uuid.uuid4()
        result = _meta_name(portfolio_id, "  Últimó Avíso #1  ")
        assert result.startswith(str(portfolio_id)[:8] + "_")
        assert " " not in result
        assert result.islower() or not any(c.isalpha() for c in result)


class TestCreate:
    async def test_creates_template_and_registers_in_meta(self):
        portfolio_id = uuid.uuid4()
        service, mocks = build_service()
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        created_template = TemplateModel(
            id=uuid.uuid4(), portfolio_id=portfolio_id, name="Recordatorio"
        )
        mocks["template_repo"].add = AsyncMock(return_value=created_template)
        mocks["client"].create_template = AsyncMock(
            return_value={"id": "meta-tpl-1", "status": "PENDING"}
        )
        created_data = WhatsAppTemplateDataModel(
            id=uuid.uuid4(),
            template_id=created_template.id,
            meta_template_id="meta-tpl-1",
            meta_name="x",
            language="es_CO",
            category=WhatsAppTemplateCategory.UTILITY,
            meta_status="PENDING",
        )
        mocks["data_repo"].add = AsyncMock(return_value=created_data)

        request = WhatsAppTemplateCreateRequest(
            name="Recordatorio",
            language="es_CO",
            category=WhatsAppTemplateCategory.UTILITY,
            components=[{"type": "BODY", "text": "Hola {{nombre}}"}],
        )

        template, whatsapp_data = await service.create(
            portfolio_id, request, ADMIN_SESSION
        )

        assert template is created_template
        assert whatsapp_data.meta_template_id == "meta-tpl-1"
        mocks["client"].create_template.assert_awaited_once()
        call_kwargs = mocks["client"].create_template.call_args.kwargs
        assert call_kwargs["category"] == "UTILITY"
        assert call_kwargs["name"].startswith(str(portfolio_id)[:8])

    async def test_meta_response_without_status_defaults_to_pending(self):
        portfolio_id = uuid.uuid4()
        service, mocks = build_service()
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].add = AsyncMock(
            return_value=TemplateModel(
                id=uuid.uuid4(), portfolio_id=portfolio_id, name="X"
            )
        )
        mocks["client"].create_template = AsyncMock(
            return_value={"id": "meta-tpl-2"}
        )  # sin "status"
        mocks["data_repo"].add = AsyncMock(side_effect=lambda m: m)

        request = WhatsAppTemplateCreateRequest(
            name="X",
            language="es_CO",
            category=WhatsAppTemplateCategory.MARKETING,
            components=[],
        )
        _template, whatsapp_data = await service.create(
            portfolio_id, request, ADMIN_SESSION
        )

        assert whatsapp_data.meta_status == "PENDING"


class TestRefreshStatus:
    async def _seed(
        self,
        service,
        mocks,
        *,
        meta_template_id="meta-1",
        meta_status="PENDING",
        template_status=TemplateStatus.DRAFT,
    ):
        template_id = uuid.uuid4()
        portfolio_id = uuid.uuid4()
        template = TemplateModel(
            id=template_id,
            portfolio_id=portfolio_id,
            name="X",
            status=template_status,
            channel=TemplateChannel.WHATSAPP,
        )
        whatsapp_data = WhatsAppTemplateDataModel(
            id=uuid.uuid4(),
            template_id=template_id,
            meta_template_id=meta_template_id,
            meta_name="x",
            language="es_CO",
            category=WhatsAppTemplateCategory.UTILITY,
            meta_status=meta_status,
        )
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].get_by_id_and_portfolio = AsyncMock(
            return_value=template
        )
        mocks["data_repo"].get_by_template_id = AsyncMock(return_value=whatsapp_data)
        mocks["template_repo"].update = AsyncMock(side_effect=lambda t: t)
        mocks["data_repo"].update = AsyncMock(side_effect=lambda d: d)
        return template_id, portfolio_id

    async def test_without_meta_template_id_short_circuits(self):
        service, mocks = build_service()
        template_id, portfolio_id = await self._seed(
            service, mocks, meta_template_id=None
        )

        template, whatsapp_data = await service.refresh_status(
            template_id, portfolio_id, ADMIN_SESSION
        )

        mocks["client"].get_template.assert_not_called()
        assert whatsapp_data.meta_status == "PENDING"

    async def test_approved_status_activates_template(self):
        service, mocks = build_service()
        template_id, portfolio_id = await self._seed(service, mocks)
        mocks["client"].get_template = AsyncMock(return_value={"status": "APPROVED"})

        template, whatsapp_data = await service.refresh_status(
            template_id, portfolio_id, ADMIN_SESSION
        )

        assert whatsapp_data.meta_status == "APPROVED"
        assert template.status == TemplateStatus.ACTIVE

    @pytest.mark.parametrize("meta_status", ["REJECTED", "PAUSED", "DISABLED"])
    async def test_inactive_statuses_deactivate_template(self, meta_status):
        service, mocks = build_service()
        template_id, portfolio_id = await self._seed(
            service, mocks, template_status=TemplateStatus.ACTIVE
        )
        mocks["client"].get_template = AsyncMock(return_value={"status": meta_status})

        template, whatsapp_data = await service.refresh_status(
            template_id, portfolio_id, ADMIN_SESSION
        )

        assert whatsapp_data.meta_status == meta_status
        assert template.status == TemplateStatus.INACTIVE

    async def test_pending_status_keeps_template_status_unchanged(self):
        service, mocks = build_service()
        template_id, portfolio_id = await self._seed(
            service, mocks, template_status=TemplateStatus.DRAFT
        )
        mocks["client"].get_template = AsyncMock(return_value={"status": "IN_APPEAL"})

        template, whatsapp_data = await service.refresh_status(
            template_id, portfolio_id, ADMIN_SESSION
        )

        assert whatsapp_data.meta_status == "IN_APPEAL"
        assert template.status == TemplateStatus.DRAFT

    async def test_template_not_found_raises_404(self):
        service, mocks = build_service()
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].get_by_id_and_portfolio = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.refresh_status(uuid.uuid4(), uuid.uuid4(), ADMIN_SESSION)
        assert exc_info.value.status_code == 404

    async def test_non_whatsapp_channel_template_raises_404(self):
        from messaging.channels.enums.channel_enums import ChannelName

        service, mocks = build_service()
        template = TemplateModel(
            id=uuid.uuid4(),
            portfolio_id=uuid.uuid4(),
            name="X",
            channel=ChannelName.EMAIL,
        )
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].get_by_id_and_portfolio = AsyncMock(
            return_value=template
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.refresh_status(uuid.uuid4(), uuid.uuid4(), ADMIN_SESSION)
        assert exc_info.value.status_code == 404

    async def test_data_row_missing_raises_404(self):
        service, mocks = build_service()
        from messaging.channels.enums.channel_enums import ChannelName

        template = TemplateModel(
            id=uuid.uuid4(),
            portfolio_id=uuid.uuid4(),
            name="X",
            channel=ChannelName.WHATSAPP,
        )
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].get_by_id_and_portfolio = AsyncMock(
            return_value=template
        )
        mocks["data_repo"].get_by_template_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.refresh_status(uuid.uuid4(), uuid.uuid4(), ADMIN_SESSION)
        assert exc_info.value.status_code == 404


class TestListVariables:
    async def test_without_meta_template_id_returns_empty_list(self):
        service, mocks = build_service()
        from messaging.channels.enums.channel_enums import ChannelName

        template = TemplateModel(
            id=uuid.uuid4(),
            portfolio_id=uuid.uuid4(),
            name="X",
            channel=ChannelName.WHATSAPP,
        )
        whatsapp_data = WhatsAppTemplateDataModel(
            id=uuid.uuid4(),
            template_id=template.id,
            meta_template_id=None,
            meta_name="x",
            language="es_CO",
            category=WhatsAppTemplateCategory.UTILITY,
        )
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].get_by_id_and_portfolio = AsyncMock(
            return_value=template
        )
        mocks["data_repo"].get_by_template_id = AsyncMock(return_value=whatsapp_data)

        result = await service.list_variables(
            template.id, template.portfolio_id, ADMIN_SESSION
        )

        assert result == []
        mocks["client"].get_template.assert_not_called()

    async def test_extracts_variables_from_live_meta_template(self):
        service, mocks = build_service()
        from messaging.channels.enums.channel_enums import ChannelName

        template = TemplateModel(
            id=uuid.uuid4(),
            portfolio_id=uuid.uuid4(),
            name="X",
            channel=ChannelName.WHATSAPP,
        )
        whatsapp_data = WhatsAppTemplateDataModel(
            id=uuid.uuid4(),
            template_id=template.id,
            meta_template_id="meta-1",
            meta_name="x",
            language="es_CO",
            category=WhatsAppTemplateCategory.UTILITY,
        )
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].get_by_id_and_portfolio = AsyncMock(
            return_value=template
        )
        mocks["data_repo"].get_by_template_id = AsyncMock(return_value=whatsapp_data)
        mocks["client"].get_template = AsyncMock(
            return_value={
                "components": [
                    {"type": "BODY", "text": "Hola {{nombre}}, debes {{monto}}"},
                ]
            }
        )

        result = await service.list_variables(
            template.id, template.portfolio_id, ADMIN_SESSION
        )

        assert [slot.name for slot in result] == ["nombre", "monto"]


class TestDelete:
    async def test_deletes_from_meta_then_local_rows(self):
        service, mocks = build_service()
        from messaging.channels.enums.channel_enums import ChannelName

        template = TemplateModel(
            id=uuid.uuid4(),
            portfolio_id=uuid.uuid4(),
            name="X",
            channel=ChannelName.WHATSAPP,
        )
        whatsapp_data = WhatsAppTemplateDataModel(
            id=uuid.uuid4(),
            template_id=template.id,
            meta_template_id="meta-1",
            meta_name="tpl_meta_name",
            language="es_CO",
            category=WhatsAppTemplateCategory.UTILITY,
        )
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].get_by_id_and_portfolio = AsyncMock(
            return_value=template
        )
        mocks["data_repo"].get_by_template_id = AsyncMock(return_value=whatsapp_data)
        mocks["client"].delete_template = AsyncMock()
        mocks["data_repo"].delete = AsyncMock()
        mocks["template_repo"].delete = AsyncMock()

        await service.delete(template.id, template.portfolio_id, ADMIN_SESSION)

        mocks["client"].delete_template.assert_awaited_once_with("tpl_meta_name")
        mocks["data_repo"].delete.assert_awaited_once_with(whatsapp_data)
        mocks["template_repo"].delete.assert_awaited_once_with(template)


def _meta_http_error(status_code: int, body: dict) -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "https://graph.facebook.com/x")
    response = httpx.Response(status_code=status_code, json=body, request=request)
    return httpx.HTTPStatusError("meta error", request=request, response=response)


class TestMetaErrorTranslation:
    """Un fallo de la Graph API debe llegar al usuario como HTTPException en español,
    no como un 500 genérico, y sin dejar filas locales a medio crear."""

    async def test_create_with_rejected_token_raises_502_and_does_not_persist_data_row(
        self,
    ):
        portfolio_id = uuid.uuid4()
        service, mocks = build_service()
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].add = AsyncMock(
            return_value=TemplateModel(
                id=uuid.uuid4(), portfolio_id=portfolio_id, name="X"
            )
        )
        mocks["client"].create_template = AsyncMock(
            side_effect=_meta_http_error(
                401, {"error": {"message": "Invalid OAuth access token.", "code": 190}}
            )
        )
        mocks["data_repo"].add = AsyncMock()

        request = WhatsAppTemplateCreateRequest(
            name="X",
            language="es",
            category=WhatsAppTemplateCategory.UTILITY,
            components=[],
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.create(portfolio_id, request, ADMIN_SESSION)

        assert exc_info.value.status_code == 502
        assert "token de acceso" in exc_info.value.detail
        mocks["data_repo"].add.assert_not_called()

    async def test_create_with_meta_validation_error_surfaces_meta_detail_as_400(self):
        portfolio_id = uuid.uuid4()
        service, mocks = build_service()
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].add = AsyncMock(
            return_value=TemplateModel(
                id=uuid.uuid4(), portfolio_id=portfolio_id, name="X"
            )
        )
        mocks["client"].create_template = AsyncMock(
            side_effect=_meta_http_error(
                400,
                {
                    "error": {
                        "message": "Invalid parameter",
                        "code": 100,
                        "error_user_msg": "El cuerpo es demasiado largo.",
                    }
                },
            )
        )

        request = WhatsAppTemplateCreateRequest(
            name="X",
            language="es",
            category=WhatsAppTemplateCategory.UTILITY,
            components=[],
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.create(portfolio_id, request, ADMIN_SESSION)

        assert exc_info.value.status_code == 400
        assert "El cuerpo es demasiado largo." in exc_info.value.detail

    async def test_refresh_status_with_network_failure_raises_502(self):
        from messaging.channels.enums.channel_enums import ChannelName

        service, mocks = build_service()
        template = TemplateModel(
            id=uuid.uuid4(),
            portfolio_id=uuid.uuid4(),
            name="X",
            channel=ChannelName.WHATSAPP,
        )
        whatsapp_data = WhatsAppTemplateDataModel(
            id=uuid.uuid4(),
            template_id=template.id,
            meta_template_id="meta-1",
            meta_name="tpl",
            language="es",
            category=WhatsAppTemplateCategory.UTILITY,
        )
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].get_by_id_and_portfolio = AsyncMock(
            return_value=template
        )
        mocks["data_repo"].get_by_template_id = AsyncMock(return_value=whatsapp_data)
        mocks["client"].get_template = AsyncMock(
            side_effect=httpx.ConnectTimeout("timeout")
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.refresh_status(
                template.id, template.portfolio_id, ADMIN_SESSION
            )

        assert exc_info.value.status_code == 502
        assert "No fue posible comunicarse con Meta" in exc_info.value.detail

    async def test_delete_keeps_local_rows_when_meta_rejects(self):
        from messaging.channels.enums.channel_enums import ChannelName

        service, mocks = build_service()
        template = TemplateModel(
            id=uuid.uuid4(),
            portfolio_id=uuid.uuid4(),
            name="X",
            channel=ChannelName.WHATSAPP,
        )
        whatsapp_data = WhatsAppTemplateDataModel(
            id=uuid.uuid4(),
            template_id=template.id,
            meta_template_id="meta-1",
            meta_name="tpl",
            language="es",
            category=WhatsAppTemplateCategory.UTILITY,
        )
        mocks["portfolio_repo"].get_by_id = AsyncMock(
            return_value=MagicMock(organization_id=uuid.uuid4())
        )
        mocks["template_repo"].get_by_id_and_portfolio = AsyncMock(
            return_value=template
        )
        mocks["data_repo"].get_by_template_id = AsyncMock(return_value=whatsapp_data)
        mocks["client"].delete_template = AsyncMock(
            side_effect=_meta_http_error(
                403, {"error": {"message": "Permissions error", "code": 200}}
            )
        )
        mocks["data_repo"].delete = AsyncMock()
        mocks["template_repo"].delete = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await service.delete(template.id, template.portfolio_id, ADMIN_SESSION)

        assert exc_info.value.status_code == 502
        mocks["data_repo"].delete.assert_not_called()
        mocks["template_repo"].delete.assert_not_called()
