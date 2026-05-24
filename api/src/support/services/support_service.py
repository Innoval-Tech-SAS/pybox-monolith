import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from notifications.services.notification_service import NotificationService
from organizations.enums.organization_enums import VerificationStatus
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from organizations.repository.organization_repository import OrganizationRepository
from support.enums.support_enums import SupportCaseType, SupportTicketStatus
from support.schemas.support_schemas import ResolveTicketSchema, SupportFilter, SupportTicketSchema
from support.models.support_ticket_model import SupportTicketModel
from support.repository.support_ticket_repository import SupportTicketRepository


class SupportService:
    def __init__(self, session: AsyncSession) -> None:
        self._ticket_repo = SupportTicketRepository(session)
        self._org_repo = OrganizationRepository(session)
        self._membership_repo = OrganizationMembershipRepository(session)
        self._notification_service = NotificationService(session)

    async def create_org_verification_ticket(
        self, org_id: uuid.UUID, created_by: int
    ) -> SupportTicketModel:
        return await self._ticket_repo.add(
            SupportTicketModel(
                case_type=SupportCaseType.ORG_VERIFICATION,
                status=SupportTicketStatus.OPEN,
                organization_id=org_id,
                created_by=created_by,
            )
        )

    async def get_all_tickets(self, f: SupportFilter) -> list[SupportTicketSchema]:
        tickets = await self._ticket_repo.get_filtered(f)
        return [SupportTicketSchema.model_validate(t) for t in tickets]

    async def get_ticket(self, ticket_id: int, f: SupportFilter) -> SupportTicketSchema:
        ticket = await self._ticket_repo.get_by_id(ticket_id)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        if f.org_ids is not None and ticket.organization_id not in f.org_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        if f.created_by is not None and ticket.created_by != f.created_by:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        return SupportTicketSchema.model_validate(ticket)

    async def resolve_ticket(
        self, ticket_id: int, agent_user_id: int, data: ResolveTicketSchema, f: SupportFilter
    ) -> SupportTicketSchema:
        if not f.can_resolve:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para resolver tickets.")
        ticket = await self._ticket_repo.get_by_id(ticket_id)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        if f.org_ids is not None and ticket.organization_id not in f.org_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        if ticket.status == SupportTicketStatus.RESOLVED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El ticket ya fue resuelto.")

        ticket.status = SupportTicketStatus.RESOLVED
        ticket.assigned_to = agent_user_id
        ticket.notes = data.notes
        ticket.resolved_at = datetime.now(timezone.utc)

        if ticket.case_type == SupportCaseType.ORG_VERIFICATION:
            org = await self._org_repo.get_by_id(ticket.organization_id)
            if org is not None:
                org.verification_status = (
                    VerificationStatus.APPROVED if data.approved else VerificationStatus.DENIED
                )
                await self._org_repo.update(org)

            await self._notify_org_verification(ticket.organization_id, ticket.created_by, data.approved)

        updated = await self._ticket_repo.update(ticket)
        return SupportTicketSchema.model_validate(updated)


    async def _notify_org_verification(
        self, org_id: uuid.UUID, ticket_created_by: int, approved: bool
    ) -> None:
        memberships = await self._membership_repo.get_by_organization_id(org_id)
        rep = next((m for m in memberships if m.is_legal_representative), None)

        recipient_ids: set[int] = {ticket_created_by}
        if rep is not None:
            recipient_ids.add(rep.user_id)

        if approved:
            title = "Empresa verificada"
            body = "Los documentos de tu empresa han sido aprobados."
        else:
            title = "Verificación rechazada"
            body = "Los documentos de tu empresa fueron rechazados. Revisa los detalles."

        for user_id in recipient_ids:
            await self._notification_service.create_notification(
                user_id=user_id,
                title=title,
                body=body,
                category="org_verification",
            )
