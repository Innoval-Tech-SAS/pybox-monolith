"""Tests unitarios de WhatsAppChannelRequestService (ver whatsapp_channel_request_service.py).

Repo mockeado. Cubre el gate de consentimiento (`ensure_case` crea el caso solo si
no existe, siempre PENDIENTE al nacer) y las transiciones de aprobar/rechazar.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from identity.users.enums.user_enums import UserRole, UserScope
from messaging.whatsapp.enums.whatsapp_enums import ChannelRequestStatus
from messaging.whatsapp.models.whatsapp_channel_request_model import WhatsAppChannelRequestModel
from messaging.whatsapp.services.whatsapp_channel_request_service import WhatsAppChannelRequestService
from tests.conftest import make_user_session

ADMIN_SESSION = make_user_session(role=UserRole.ADMIN, scope=UserScope.GLOBAL)


def build_service() -> tuple[WhatsAppChannelRequestService, MagicMock]:
    repo = MagicMock()
    return WhatsAppChannelRequestService(repo), repo


class TestEnsureCase:
    async def test_existing_case_returns_its_current_status_without_creating(self):
        organization_id = uuid.uuid4()
        existing = WhatsAppChannelRequestModel(
            organization_id=organization_id, phone="573000000000", status=ChannelRequestStatus.APPROVED
        )
        service, repo = build_service()
        repo.get_by_org_and_phone = AsyncMock(return_value=existing)

        status = await service.ensure_case(organization_id, "573000000000")

        assert status == ChannelRequestStatus.APPROVED
        repo.add.assert_not_called()

    async def test_new_phone_creates_pending_case(self):
        organization_id = uuid.uuid4()
        debtor_id = uuid.uuid4()
        service, repo = build_service()
        repo.get_by_org_and_phone = AsyncMock(return_value=None)
        repo.add = AsyncMock(
            side_effect=lambda model: WhatsAppChannelRequestModel(
                organization_id=model.organization_id,
                phone=model.phone,
                debtor_id=model.debtor_id,
                status=ChannelRequestStatus.PENDING,
            )
        )

        status = await service.ensure_case(organization_id, "573000000000", debtor_id=debtor_id)

        assert status == ChannelRequestStatus.PENDING
        added_model = repo.add.call_args.args[0]
        assert added_model.debtor_id == debtor_id


class TestGetExistingStatuses:
    async def test_maps_by_phone_only_for_phones_with_a_case(self):
        organization_id = uuid.uuid4()
        service, repo = build_service()
        repo.get_by_org_and_phones = AsyncMock(
            return_value=[
                WhatsAppChannelRequestModel(
                    organization_id=organization_id, phone="573000000001", status=ChannelRequestStatus.APPROVED
                ),
            ]
        )

        result = await service.get_existing_statuses(organization_id, ["573000000001", "573000000002"])

        assert result == {"573000000001": ChannelRequestStatus.APPROVED}
        assert "573000000002" not in result


class TestApproveReject:
    async def test_approve_sets_status_and_resolver(self):
        organization_id = uuid.uuid4()
        case = WhatsAppChannelRequestModel(
            organization_id=organization_id, phone="573000000000", status=ChannelRequestStatus.PENDING
        )
        service, repo = build_service()
        repo.get_by_id = AsyncMock(return_value=case)
        repo.update = AsyncMock(side_effect=lambda c: c)

        result = await service.approve(uuid.uuid4(), organization_id, ADMIN_SESSION)

        assert result.status == ChannelRequestStatus.APPROVED
        assert result.resolved_by == ADMIN_SESSION.user_id
        assert result.resolved_at is not None

    async def test_reject_sets_status_and_resolver(self):
        organization_id = uuid.uuid4()
        case = WhatsAppChannelRequestModel(
            organization_id=organization_id, phone="573000000000", status=ChannelRequestStatus.PENDING
        )
        service, repo = build_service()
        repo.get_by_id = AsyncMock(return_value=case)
        repo.update = AsyncMock(side_effect=lambda c: c)

        result = await service.reject(uuid.uuid4(), organization_id, ADMIN_SESSION)

        assert result.status == ChannelRequestStatus.REJECTED
        assert result.resolved_by == ADMIN_SESSION.user_id

    async def test_case_not_found_raises_404(self):
        service, repo = build_service()
        repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.approve(uuid.uuid4(), uuid.uuid4(), ADMIN_SESSION)
        assert exc_info.value.status_code == 404

    async def test_case_from_other_organization_raises_404(self):
        case = WhatsAppChannelRequestModel(
            organization_id=uuid.uuid4(), phone="573000000000", status=ChannelRequestStatus.PENDING
        )
        service, repo = build_service()
        repo.get_by_id = AsyncMock(return_value=case)

        with pytest.raises(HTTPException) as exc_info:
            await service.reject(uuid.uuid4(), uuid.uuid4(), ADMIN_SESSION)
        assert exc_info.value.status_code == 404

    async def test_approve_requires_org_admin(self):
        organization_id = uuid.uuid4()
        service, repo = build_service()
        agent_session = make_user_session(role=UserRole.USER, scope=UserScope.ORGANIZATION, orgs={})

        with pytest.raises(HTTPException) as exc_info:
            await service.approve(uuid.uuid4(), organization_id, agent_session)
        assert exc_info.value.status_code == 403
        repo.get_by_id.assert_not_called()


class TestListByOrg:
    async def test_delegates_to_repo_with_filters(self):
        organization_id = uuid.uuid4()
        service, repo = build_service()
        repo.list_by_organization = AsyncMock(return_value=([], 0))

        await service.list_by_org(organization_id, 1, 20, ADMIN_SESSION, ChannelRequestStatus.PENDING)

        repo.list_by_organization.assert_awaited_once_with(organization_id, 1, 20, ChannelRequestStatus.PENDING)

    async def test_requires_org_admin(self):
        service, repo = build_service()
        agent_session = make_user_session(role=UserRole.USER, scope=UserScope.ORGANIZATION, orgs={})

        with pytest.raises(HTTPException) as exc_info:
            await service.list_by_org(uuid.uuid4(), 1, 20, agent_session)
        assert exc_info.value.status_code == 403
