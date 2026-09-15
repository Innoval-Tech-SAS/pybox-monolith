import uuid

from core.security.policies.security_policies import require_org_admin
from identity.users.schemas.user_session_schema import UserSession
from messaging.whatsapp.models.whatsapp_send_error_model import WhatsAppSendErrorModel
from messaging.whatsapp.repository.whatsapp_send_error_repository import WhatsAppSendErrorRepository


class WhatsAppErrorService:

    def __init__(self, repo: WhatsAppSendErrorRepository) -> None:
        self._repo = repo

    async def list_by_org(
        self, organization_id: uuid.UUID, page: int, page_size: int, user_session: UserSession
    ) -> tuple[list[WhatsAppSendErrorModel], int]:
        require_org_admin(user_session, str(organization_id))
        return await self._repo.list_by_organization(organization_id, page, page_size)
