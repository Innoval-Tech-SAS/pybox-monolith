import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status

from core.security.policies.security_policies import require_org_admin
from identity.users.schemas.user_session_schema import UserSession
from messaging.whatsapp.enums.whatsapp_enums import ChannelRequestStatus
from messaging.whatsapp.models.whatsapp_channel_request_model import WhatsAppChannelRequestModel
from messaging.whatsapp.repository.whatsapp_channel_request_repository import WhatsAppChannelRequestRepository


class WhatsAppChannelRequestService:

    def __init__(self, repo: WhatsAppChannelRequestRepository) -> None:
        self._repo = repo

    async def ensure_case(
        self,
        organization_id: uuid.UUID,
        phone: str,
        debtor_id: uuid.UUID | None = None,
        origin_campaign_id: uuid.UUID | None = None,
    ) -> ChannelRequestStatus:
        """Gate de consentimiento: crea el caso si no existe (queda PENDIENTE) y
        devuelve el estado vigente. Un envío solo procede si el estado es APROBADA."""
        existing = await self._repo.get_by_org_and_phone(organization_id, phone)
        if existing is not None:
            return existing.status

        created = await self._repo.add(
            WhatsAppChannelRequestModel(
                organization_id=organization_id,
                phone=phone,
                debtor_id=debtor_id,
                origin_campaign_id=origin_campaign_id,
            )
        )
        return created.status

    async def get_existing_statuses(
        self, organization_id: uuid.UUID, phones: list[str]
    ) -> dict[str, ChannelRequestStatus]:
        """Prefetch en batch el estado de consentimiento de varios teléfonos, para no
        consultar uno por uno en envíos masivos. Los teléfonos sin caso previo no
        aparecen en el resultado — siguen requiriendo ensure_case para crearlos."""
        existing = await self._repo.get_by_org_and_phones(organization_id, phones)
        return {case.phone: case.status for case in existing}

    async def ensure_cases_bulk(
        self,
        organization_id: uuid.UUID,
        phone_to_debtor_id: dict[str, uuid.UUID | None],
        origin_campaign_id: uuid.UUID | None = None,
    ) -> None:
        """Versión en lote de `ensure_case`, para teléfonos que `get_existing_statuses`
        ya confirmó que NO tienen caso previo (Fase 6 de la auditoría: evita el
        `ensure_case` -- 1 SELECT/INSERT -- dentro del loop de destinatarios de
        `automation_service`). Un solo INSERT multi-fila; quedan PENDIENTE por
        default, igual que un `ensure_case` que crea uno nuevo."""
        if not phone_to_debtor_id:
            return
        cases = [
            WhatsAppChannelRequestModel(
                organization_id=organization_id,
                phone=phone,
                debtor_id=debtor_id,
                origin_campaign_id=origin_campaign_id,
            )
            for phone, debtor_id in phone_to_debtor_id.items()
        ]
        await self._repo.add_many_isolated(cases)

    async def list_by_org(
        self,
        organization_id: uuid.UUID,
        page: int,
        page_size: int,
        user_session: UserSession,
        request_status: ChannelRequestStatus | None = None,
    ) -> tuple[list[WhatsAppChannelRequestModel], int]:
        require_org_admin(user_session, str(organization_id))
        return await self._repo.list_by_organization(organization_id, page, page_size, request_status)

    async def _resolve(
        self, request_id: uuid.UUID, organization_id: uuid.UUID, user_session: UserSession
    ) -> WhatsAppChannelRequestModel:
        require_org_admin(user_session, str(organization_id))
        case = await self._repo.get_by_id(request_id)
        if case is None or case.organization_id != organization_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Solicitud no encontrada")
        return case

    async def approve(
        self, request_id: uuid.UUID, organization_id: uuid.UUID, user_session: UserSession
    ) -> WhatsAppChannelRequestModel:
        case = await self._resolve(request_id, organization_id, user_session)
        case.status = ChannelRequestStatus.APPROVED
        case.resolved_by = user_session.user_id
        case.resolved_at = datetime.now(timezone.utc)
        return await self._repo.update(case)

    async def reject(
        self, request_id: uuid.UUID, organization_id: uuid.UUID, user_session: UserSession
    ) -> WhatsAppChannelRequestModel:
        case = await self._resolve(request_id, organization_id, user_session)
        case.status = ChannelRequestStatus.REJECTED
        case.resolved_by = user_session.user_id
        case.resolved_at = datetime.now(timezone.utc)
        return await self._repo.update(case)
