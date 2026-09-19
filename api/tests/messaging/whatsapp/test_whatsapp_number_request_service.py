"""Tests unitarios de WhatsAppNumberRequestService (ver whatsapp_number_request_service.py).

Repo y SupportService mockeados. Cubre `has_active_number` (ninguna fila / fila
inactiva / fila activa) y que `ensure_number_available` solo abra un ticket de
soporte cuando la organización no tiene número activo, sin lanzar excepción.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

from messaging.whatsapp.models.whatsapp_org_credentials_model import WhatsAppOrgCredentialsModel
from messaging.whatsapp.services.whatsapp_number_request_service import WhatsAppNumberRequestService


def build_service() -> tuple[WhatsAppNumberRequestService, MagicMock, MagicMock]:
    credentials_repo = MagicMock()
    support_service = MagicMock()
    return WhatsAppNumberRequestService(credentials_repo, support_service), credentials_repo, support_service


class TestHasActiveNumber:
    async def test_no_credentials_row_returns_false(self):
        service, credentials_repo, _support = build_service()
        credentials_repo.get_by_organization = AsyncMock(return_value=None)

        assert await service.has_active_number(uuid.uuid4()) is False

    async def test_inactive_credentials_returns_false(self):
        service, credentials_repo, _support = build_service()
        credentials_repo.get_by_organization = AsyncMock(
            return_value=WhatsAppOrgCredentialsModel(organization_id=uuid.uuid4(), phone_number_id="1", active=False)
        )

        assert await service.has_active_number(uuid.uuid4()) is False

    async def test_active_credentials_returns_true(self):
        service, credentials_repo, _support = build_service()
        credentials_repo.get_by_organization = AsyncMock(
            return_value=WhatsAppOrgCredentialsModel(organization_id=uuid.uuid4(), phone_number_id="1", active=True)
        )

        assert await service.has_active_number(uuid.uuid4()) is True


class TestEnsureNumberAvailable:
    async def test_already_has_number_returns_true_without_opening_ticket(self):
        organization_id = uuid.uuid4()
        service, credentials_repo, support_service = build_service()
        credentials_repo.get_by_organization = AsyncMock(
            return_value=WhatsAppOrgCredentialsModel(organization_id=organization_id, phone_number_id="1", active=True)
        )

        result = await service.ensure_number_available(organization_id, uuid.uuid4())

        assert result is True
        support_service.ensure_whatsapp_number_ticket.assert_not_called()

    async def test_without_number_opens_ticket_and_returns_false(self):
        organization_id = uuid.uuid4()
        requested_by = uuid.uuid4()
        service, credentials_repo, support_service = build_service()
        credentials_repo.get_by_organization = AsyncMock(return_value=None)
        support_service.ensure_whatsapp_number_ticket = AsyncMock()

        result = await service.ensure_number_available(organization_id, requested_by)

        assert result is False
        support_service.ensure_whatsapp_number_ticket.assert_awaited_once_with(organization_id, requested_by)
