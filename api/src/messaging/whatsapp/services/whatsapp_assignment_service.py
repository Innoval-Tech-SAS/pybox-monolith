import uuid

from core.security.constants.permissions import MANAGE_WHATSAPP_CHATS
from identity.users.repository.permission_assignment_repository import (
    PermissionAssignmentRepository,
)
from messaging.whatsapp.models.whatsapp_chat_model import WhatsAppChatModel
from messaging.whatsapp.repository.whatsapp_chat_repository import (
    WhatsAppChatRepository,
)
from receivables.portfolios.repository.portfolio_user_access_repository import (
    PortfolioUserAccessRepository,
)


class WhatsAppAssignmentService:
    """Auto-asignación de un hilo nuevo a un agente de WhatsApp de la organización
    (usuario USER/ORGANIZATION con el permiso MANAGE_WHATSAPP_CHATS otorgado), acotado
    a los que además tienen acceso al portafolio del hilo."""

    def __init__(
        self,
        chat_repo: WhatsAppChatRepository,
        permission_repo: PermissionAssignmentRepository,
        portfolio_access_repo: PortfolioUserAccessRepository,
    ) -> None:
        self._chat_repo = chat_repo
        self._permission_repo = permission_repo
        self._portfolio_access_repo = portfolio_access_repo

    async def assign(
        self, chat: WhatsAppChatModel, organization_id: uuid.UUID
    ) -> WhatsAppChatModel:
        candidate_ids = await self._permission_repo.get_user_ids_with_permission_in_org(
            organization_id, MANAGE_WHATSAPP_CHATS
        )
        if chat.portfolio_id is None:
            # Sin portafolio resuelto (el deudor escribió sin envío previo asociado): no
            # se autoasigna a nadie, queda visible solo para admins hasta reasignación
            # manual — ver whatsapp_chat_service._get_chat_for_user.
            candidate_ids = []
        else:
            portfolio_user_ids = set(
                await self._portfolio_access_repo.get_active_user_ids_for_portfolio(
                    chat.portfolio_id
                )
            )
            candidate_ids = [
                user_id for user_id in candidate_ids if user_id in portfolio_user_ids
            ]
        # Sin candidatos elegibles, el hilo queda sin asignar (visible
        # solo para admins hasta que se agregue un agente con acceso al
        # portafolio o se reasigne manualmente).
        chat.assigned_user_id = await self._chat_repo.get_least_loaded_user(
            candidate_ids
        )
        return await self._chat_repo.update(chat)
