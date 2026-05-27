import os
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.paths import UPLOADS_ROOT

from notifications.services.notification_service import NotificationService
from organizations.enums.organization_enums import VerificationStatus
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from organizations.repository.organization_repository import OrganizationRepository
from support.enums.support_enums import SupportCaseType, SupportTicketStatus
from support.models.support_ticket_model import SupportTicketModel
from support.repository.support_ticket_repository import SupportTicketRepository
from support.schemas.support_schemas import AssignTicketSchema, OrgDocSchema, OrgDocsSchema, ResolveTicketSchema, SupportFilter, SupportTicketSchema


class SupportService:
    def __init__(self, session: AsyncSession) -> None:
        self._ticket_repo = SupportTicketRepository(session)
        self._org_repo = OrganizationRepository(session)
        self._membership_repo = OrganizationMembershipRepository(session)
        self._notification_service = NotificationService(session)

    async def create_org_verification_ticket(
        self, org_id: uuid.UUID, created_by: int
    ) -> SupportTicketModel:
        ticket = await self._ticket_repo.add(
            SupportTicketModel(
                case_type=SupportCaseType.ORG_VERIFICATION,
                status=SupportTicketStatus.OPEN,
                organization_id=org_id,
                created_by=created_by,
            )
        )
        await self._auto_assign(ticket)
        return ticket

    async def get_all_tickets(self, f: SupportFilter) -> list[SupportTicketSchema]:
        tickets = await self._ticket_repo.get_filtered(f)
        return [SupportTicketSchema.model_validate(t) for t in tickets]

    async def get_ticket(self, ticket_number: int, f: SupportFilter) -> SupportTicketSchema:
        ticket = await self._ticket_repo.get_by_ticket_number(ticket_number)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        if f.org_ids is not None and ticket.organization_id not in f.org_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        if f.created_by is not None and ticket.created_by != f.created_by:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        return SupportTicketSchema.model_validate(ticket)

    async def resolve_ticket(
        self, ticket_number: int, agent_user_id: int, data: ResolveTicketSchema, f: SupportFilter
    ) -> SupportTicketSchema:
        if not f.can_resolve:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para resolver tickets.")
        ticket = await self._ticket_repo.get_by_ticket_number(ticket_number)
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

    async def get_org_docs(self, ticket_number: int, f: SupportFilter) -> OrgDocsSchema:
        if not f.can_resolve:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        ticket = await self._ticket_repo.get_by_ticket_number(ticket_number)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        if ticket.case_type != SupportCaseType.ORG_VERIFICATION:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este ticket no es de verificación.")
        org = await self._org_repo.get_by_id(ticket.organization_id)
        if org is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada.")

        def _url(path: str | None) -> str | None:
            if not path:
                return None
            norm = path.replace("\\", "/")
            abs_root = os.path.abspath(UPLOADS_ROOT)
            abs_path = os.path.abspath(norm)
            try:
                rel = os.path.relpath(abs_path, abs_root)
                if not rel.startswith(".."):
                    return "/files/" + rel.replace(os.sep, "/")
            except ValueError:
                pass
            return "/files/" + norm

        return OrgDocsSchema(
            org_name=org.name,
            documents=[
                OrgDocSchema(label="Documento fiscal", url=_url(org.fiscal_document_file)),
                OrgDocSchema(label="Documento mercantil", url=_url(org.mercantile_document_file)),
                OrgDocSchema(label="Documento representante", url=_url(org.representative_document_file)),
            ],
        )

    async def assign_ticket(
        self, ticket_number: int, data: AssignTicketSchema, f: SupportFilter
    ) -> SupportTicketSchema:
        if not f.can_assign:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para asignar tickets.")
        ticket = await self._ticket_repo.get_by_ticket_number(ticket_number)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        if f.org_ids is not None and ticket.organization_id not in f.org_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        if ticket.status == SupportTicketStatus.RESOLVED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede reasignar un ticket resuelto.")

        ticket.assigned_to = data.user_id
        ticket.status = SupportTicketStatus.IN_PROGRESS
        updated = await self._ticket_repo.update(ticket)

        await self._notification_service.create_notification(
            user_id=data.user_id,
            title="Ticket asignado",
            body=f"Se te asignó el ticket de soporte #{ticket.ticket_number}.",
            category="support",
            notif_type="info",
            link=f"/cs/tickets/{ticket.ticket_number}",
        )
        return SupportTicketSchema.model_validate(updated)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _auto_assign(self, ticket: SupportTicketModel) -> None:
        agent_id = await self._ticket_repo.find_least_loaded_cs_org(ticket.organization_id)
        if agent_id is None:
            agent_id = await self._ticket_repo.find_least_loaded_cs_global()
        if agent_id is None:
            return

        ticket.assigned_to = agent_id
        ticket.status = SupportTicketStatus.IN_PROGRESS
        await self._ticket_repo.update(ticket)

        await self._notification_service.create_notification(
            user_id=agent_id,
            title="Nuevo ticket asignado",
            body=f"Se te asignó un ticket de soporte #{ticket.ticket_number}.",
            category="support",
            notif_type="info",
            link=f"/cs/tickets/{ticket.ticket_number}",
        )

    async def _notify_org_verification(
        self, org_id: uuid.UUID, ticket_created_by: int, approved: bool
    ) -> None:
        memberships = await self._membership_repo.get_by_organization_id(org_id)
        rep = next((m for m in memberships if m.is_legal_representative), None)

        recipient_ids: set[int] = {ticket_created_by}
        if rep is not None:
            recipient_ids.add(rep.user_id)

        title = "Empresa verificada" if approved else "Verificación rechazada"
        body = (
            "Los documentos de tu empresa han sido aprobados."
            if approved
            else "Los documentos de tu empresa fueron rechazados. Revisa los detalles."
        )

        for user_id in recipient_ids:
            await self._notification_service.create_notification(
                user_id=user_id,
                title=title,
                body=body,
                category="org_verification",
            )
