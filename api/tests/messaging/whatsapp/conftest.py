"""Fixtures y builders compartidos por los tests de `messaging.whatsapp`.

No hay endpoint para crear una organización mínima sin pasar por todo el flujo de
registro + verificación (ver `tests/receivables/conftest.py`, mismo patrón) -- para
los tests de este módulo alcanza con una fila real de `entidades` insertada directo
por SQLAlchemy, porque casi todas las validaciones de permisos las esquiva un usuario
global (`make_user_session_factory(scope=UserScope.GLOBAL)`).
"""

import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
import pytest_asyncio

from identity.organizations.enums.organization_enums import (
    EntitySectors,
    VerificationStatus,
)
from identity.organizations.models.organization_model import OrganizationModel
from messaging.channels.enums.channel_enums import ChannelName
from messaging.templates.enums.template_enums import TemplateStatus
from messaging.templates.models.template_model import TemplateModel
from messaging.whatsapp.enums.whatsapp_enums import (
    ChannelRequestStatus,
    MessageDirection,
    WhatsAppTemplateCategory,
)
from messaging.whatsapp.models.whatsapp_chat_model import WhatsAppChatModel
from messaging.whatsapp.models.whatsapp_channel_request_model import (
    WhatsAppChannelRequestModel,
)
from messaging.whatsapp.models.whatsapp_message_model import WhatsAppMessageModel
from messaging.whatsapp.models.whatsapp_org_credentials_model import (
    WhatsAppOrgCredentialsModel,
)
from messaging.whatsapp.models.whatsapp_send_error_model import WhatsAppSendErrorModel
from messaging.whatsapp.models.whatsapp_template_data_model import (
    WhatsAppTemplateDataModel,
)
from receivables.portfolios.models.portfolio_model import PortfolioModel
from tests.factories import get_user_by_email, register_payload, unique_phone


def build_organization(**overrides: Any) -> OrganizationModel:
    defaults = dict(
        name=f"Org {uuid.uuid4().hex[:8]}",
        sector=EntitySectors.FINTECH,
        verification_status=VerificationStatus.APPROVED,
    )
    defaults.update(overrides)
    return OrganizationModel(**defaults)


@pytest_asyncio.fixture
async def real_org(db_session) -> OrganizationModel:
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    return org


def build_credentials(
    organization_id: uuid.UUID, **overrides: Any
) -> WhatsAppOrgCredentialsModel:
    defaults = dict(
        organization_id=organization_id,
        phone_number_id=str(uuid.uuid4().int)[:15],
        display_name="Línea de cobranza",
        active=True,
    )
    defaults.update(overrides)
    return WhatsAppOrgCredentialsModel(**defaults)


def build_chat(organization_id: uuid.UUID, **overrides: Any) -> WhatsAppChatModel:
    defaults = dict(
        organization_id=organization_id,
        phone=unique_phone(),
        profile_name="Juan Deudor",
    )
    defaults.update(overrides)
    return WhatsAppChatModel(**defaults)


def build_message(chat_id: uuid.UUID, **overrides: Any) -> WhatsAppMessageModel:
    defaults = dict(
        chat_id=chat_id,
        direction=MessageDirection.INBOUND,
        wamid=f"wamid.{uuid.uuid4().hex[:12]}",
        message_type="text",
        content="hola",
        raw_payload={"type": "text", "text": {"body": "hola"}},
        sent_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return WhatsAppMessageModel(**defaults)


def build_channel_request(
    organization_id: uuid.UUID, **overrides: Any
) -> WhatsAppChannelRequestModel:
    defaults = dict(
        organization_id=organization_id,
        phone=unique_phone(),
        status=ChannelRequestStatus.PENDING,
    )
    defaults.update(overrides)
    return WhatsAppChannelRequestModel(**defaults)


def build_send_error(**overrides: Any) -> WhatsAppSendErrorModel:
    defaults = dict(
        error_code=131047,
        message="(#131047) Message failed to send because more than 24 hours have passed",
        raw_payload={"code": 131047},
        occurred_at=datetime.now(timezone.utc),
    )
    defaults.update(overrides)
    return WhatsAppSendErrorModel(**defaults)


def build_template(portfolio_id: uuid.UUID, **overrides: Any) -> TemplateModel:
    defaults = dict(
        portfolio_id=portfolio_id,
        name=f"Plantilla {uuid.uuid4().hex[:6]}",
        channel=ChannelName.WHATSAPP,
        status=TemplateStatus.DRAFT,
        body=None,
    )
    defaults.update(overrides)
    return TemplateModel(**defaults)


def build_template_data(
    template_id: uuid.UUID, **overrides: Any
) -> WhatsAppTemplateDataModel:
    defaults = dict(
        template_id=template_id,
        meta_template_id=str(uuid.uuid4().int)[:15],
        meta_name=f"tpl_{uuid.uuid4().hex[:8]}",
        language="es_CO",
        category=WhatsAppTemplateCategory.UTILITY,
        meta_status="PENDING",
    )
    defaults.update(overrides)
    return WhatsAppTemplateDataModel(**defaults)


@pytest_asyncio.fixture
async def real_portfolio(db_session, real_org) -> PortfolioModel:
    portfolio = PortfolioModel(
        name=f"Portafolio {uuid.uuid4().hex[:8]}",
        organization_id=real_org.id,
        country="CO",
    )
    db_session.add(portfolio)
    await db_session.flush()
    return portfolio


@pytest.fixture
def make_real_user_id(client, db_session):
    """Fábrica async `await make_real_user_id()` -> uuid de un usuario real recién
    registrado. `assigned_user_id`/`resolved_by` son FKs reales a `usuarios.id`: un
    uuid inventado revienta el INSERT con ForeignKeyViolationError (ver mismo
    patrón en `tests/receivables/conftest.py::real_admin_user_id`).
    """

    async def _make() -> uuid.UUID:
        payload = register_payload()
        resp = await client.post("/api/v1/auth/register/user", json=payload)
        assert resp.status_code == 201
        user = await get_user_by_email(db_session, payload["email"])
        client.cookies.clear()
        return user.id

    return _make
