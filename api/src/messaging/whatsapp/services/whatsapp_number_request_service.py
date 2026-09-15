import uuid

from app_platform.support.services.support_service import SupportService
from messaging.whatsapp.repository.whatsapp_org_credentials_repository import WhatsAppOrgCredentialsRepository


class WhatsAppNumberRequestService:
    """Puente entre WhatsApp y el sistema de tickets de soporte: si una organización
    intenta registrar/activar/enviar una campaña de WhatsApp sin tener un número
    configurado, se crea (o reutiliza, si ya hay uno abierto) un ticket asignado a
    un agente de servicio al cliente de scope global — mismo patrón que la
    validación de documentos de empresa.
    """

    def __init__(
        self,
        credentials_repo: WhatsAppOrgCredentialsRepository,
        support_service: SupportService,
    ) -> None:
        self._credentials_repo = credentials_repo
        self._support_service = support_service

    async def has_active_number(self, organization_id: uuid.UUID) -> bool:
        credentials = await self._credentials_repo.get_by_organization(organization_id)
        return credentials is not None and credentials.active

    async def ensure_number_available(self, organization_id: uuid.UUID, requested_by: uuid.UUID) -> bool:
        """Devuelve True si la org ya tiene número. Si no, crea (o reutiliza) el
        ticket de solicitud y devuelve False — no lanza excepción, cada caller
        decide si eso bloquea la operación o solo la deja pendiente."""
        if await self.has_active_number(organization_id):
            return True
        await self._support_service.ensure_whatsapp_number_ticket(organization_id, requested_by)
        return False
