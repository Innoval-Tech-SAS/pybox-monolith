"""Tests unitarios de WhatsAppAssignmentService (ver whatsapp_assignment_service.py).

Repos mockeados. Cubre las tres ramas de auto-asignación: hilo sin portafolio
resuelto (nunca se asigna a nadie), candidatos con permiso pero sin acceso al
portafolio (se filtran), y el camino feliz delegando en `get_least_loaded_user`.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

from messaging.whatsapp.models.whatsapp_chat_model import WhatsAppChatModel
from messaging.whatsapp.services.whatsapp_assignment_service import WhatsAppAssignmentService


def build_service(**overrides) -> tuple[WhatsAppAssignmentService, dict]:
    mocks = dict(chat_repo=MagicMock(), permission_repo=MagicMock(), portfolio_access_repo=MagicMock())
    mocks.update(overrides)
    return WhatsAppAssignmentService(**mocks), mocks


class TestAssign:
    async def test_chat_without_portfolio_is_never_assigned(self):
        organization_id = uuid.uuid4()
        chat = WhatsAppChatModel(
            id=uuid.uuid4(), organization_id=organization_id, phone="573000000000", portfolio_id=None
        )
        service, mocks = build_service()
        mocks["permission_repo"].get_user_ids_with_permission_in_org = AsyncMock(
            return_value=[uuid.uuid4(), uuid.uuid4()]
        )
        mocks["chat_repo"].get_least_loaded_user = AsyncMock(return_value=None)
        mocks["chat_repo"].update = AsyncMock(side_effect=lambda c: c)

        result = await service.assign(chat, organization_id)

        assert result.assigned_user_id is None
        # candidate_ids se vacía explícitamente sin portafolio -- nunca se consulta
        # accesos_usuario_portafolio.
        mocks["portfolio_access_repo"].get_active_user_ids_for_portfolio.assert_not_called()
        mocks["chat_repo"].get_least_loaded_user.assert_awaited_once_with([])

    async def test_candidates_without_portfolio_access_are_filtered_out(self):
        organization_id = uuid.uuid4()
        portfolio_id = uuid.uuid4()
        chat = WhatsAppChatModel(
            id=uuid.uuid4(), organization_id=organization_id, phone="573000000000", portfolio_id=portfolio_id
        )
        agent_with_access = uuid.uuid4()
        agent_without_access = uuid.uuid4()
        service, mocks = build_service()
        mocks["permission_repo"].get_user_ids_with_permission_in_org = AsyncMock(
            return_value=[agent_with_access, agent_without_access]
        )
        mocks["portfolio_access_repo"].get_active_user_ids_for_portfolio = AsyncMock(
            return_value=[agent_with_access]
        )
        mocks["chat_repo"].get_least_loaded_user = AsyncMock(return_value=agent_with_access)
        mocks["chat_repo"].update = AsyncMock(side_effect=lambda c: c)

        result = await service.assign(chat, organization_id)

        assert result.assigned_user_id == agent_with_access
        mocks["chat_repo"].get_least_loaded_user.assert_awaited_once_with([agent_with_access])

    async def test_no_eligible_candidates_leaves_chat_unassigned(self):
        organization_id = uuid.uuid4()
        portfolio_id = uuid.uuid4()
        chat = WhatsAppChatModel(
            id=uuid.uuid4(), organization_id=organization_id, phone="573000000000", portfolio_id=portfolio_id
        )
        service, mocks = build_service()
        mocks["permission_repo"].get_user_ids_with_permission_in_org = AsyncMock(return_value=[uuid.uuid4()])
        mocks["portfolio_access_repo"].get_active_user_ids_for_portfolio = AsyncMock(return_value=[])
        mocks["chat_repo"].get_least_loaded_user = AsyncMock(return_value=None)
        mocks["chat_repo"].update = AsyncMock(side_effect=lambda c: c)

        result = await service.assign(chat, organization_id)

        assert result.assigned_user_id is None

    async def test_updates_chat_with_resolved_assignee(self):
        organization_id = uuid.uuid4()
        portfolio_id = uuid.uuid4()
        agent_id = uuid.uuid4()
        chat = WhatsAppChatModel(
            id=uuid.uuid4(), organization_id=organization_id, phone="573000000000", portfolio_id=portfolio_id
        )
        service, mocks = build_service()
        mocks["permission_repo"].get_user_ids_with_permission_in_org = AsyncMock(return_value=[agent_id])
        mocks["portfolio_access_repo"].get_active_user_ids_for_portfolio = AsyncMock(return_value=[agent_id])
        mocks["chat_repo"].get_least_loaded_user = AsyncMock(return_value=agent_id)
        mocks["chat_repo"].update = AsyncMock(side_effect=lambda c: c)

        result = await service.assign(chat, organization_id)

        assert result.assigned_user_id == agent_id
        mocks["chat_repo"].update.assert_awaited_once_with(chat)
