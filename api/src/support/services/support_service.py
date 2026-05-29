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
from portfolios.repository.portfolio_user_access_repository import PortfolioUserAccessRepository
from support.enums.support_enums import SupportCaseType, SupportTicketStatus
from support.models.support_ticket_model import SupportTicketModel
from support.repository.support_ticket_repository import SupportTicketRepository
from support.schemas.support_schemas import AssignTicketSchema, CreateTicketSchema, OrgDocSchema, OrgDocsSchema, ResolveTicketSchema, SupportFilter, SupportTicketSchema, TicketOrgSchema, UpdateTicketStatusSchema
from users.schemas.user_session_schema import UserSession


class SupportService:
    def __init__(self, session: AsyncSession) -> None:
        self._ticket_repo = SupportTicketRepository(session)
        self._org_repo = OrganizationRepository(session)
        self._membership_repo = OrganizationMembershipRepository(session)
        self._portfolio_access_repo = PortfolioUserAccessRepository(session)
        self._notification_service = NotificationService(session)

    async def create_org_verification_ticket(
        self, org_id: uuid.UUID, created_by: int
    ) -> SupportTicketModel:
        org = await self._org_repo.get_by_id(org_id)
        org_name = org.name if org else "empresa"
        ticket = await self._ticket_repo.add(
            SupportTicketModel(
                case_type=SupportCaseType.REQUIREMENT,
                status=SupportTicketStatus.OPEN,
                organization_id=org_id,
                created_by=created_by,
                title=f"Validación de Documentos {org_name}",
                notes=f"Ticket creado automáticamente al registrar empresa: {org_name}. Se debe realizar la verificación documental.",
            )
        )
        await self._auto_assign(ticket)
        return ticket

    async def get_all_tickets(self, f: SupportFilter) -> list[SupportTicketSchema]:
        tickets = await self._ticket_repo.get_filtered(f)
        result = []
        for t in tickets:
            result.append(await self._ticket_to_schema(t))
        return result

    async def get_ticket(self, ticket_number: int, f: SupportFilter) -> SupportTicketSchema:
        ticket = await self._ticket_repo.get_by_ticket_number(ticket_number)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        if f.org_ids is not None and ticket.organization_id not in f.org_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        if f.created_by is not None and ticket.created_by != f.created_by:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        return await self._ticket_to_schema(ticket)

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

        if ticket.case_type == SupportCaseType.REQUIREMENT:
            org = await self._org_repo.get_by_id(ticket.organization_id)
            if org is not None:
                org.verification_status = (
                    VerificationStatus.APPROVED if data.approved else VerificationStatus.DENIED
                )
                await self._org_repo.update(org)

            await self._notify_org_verification(ticket.organization_id, ticket.created_by, data.approved)

        updated = await self._ticket_repo.update(ticket)
        return await self._ticket_to_schema(updated)

    async def get_ticket_orgs(self, session: UserSession) -> list[TicketOrgSchema]:
        if session.is_self:
            org_ids = await self._portfolio_access_repo.get_distinct_org_ids_by_user(session.user_id)
            result = []
            for org_id in org_ids:
                org = await self._org_repo.get_by_id(org_id)
                if org:
                    result.append(TicketOrgSchema(id=org.id, name=org.name))
            return result
        return [
            TicketOrgSchema(id=uuid.UUID(org_id), name=entry.org_name)
            for org_id, entry in session.orgs.items()
        ]

    async def create_ticket(self, user_id: int, data: CreateTicketSchema, f: SupportFilter) -> SupportTicketSchema:
        if not f.can_create:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para crear tickets.")

        if f.check_portfolio_access:
            accesses = await self._portfolio_access_repo.get_active_by_user_and_org(user_id, data.organization_id)
            if not accesses:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta entidad.")
        elif f.org_ids is not None and data.organization_id not in f.org_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta entidad.")

        ticket = SupportTicketModel(
            case_type=SupportCaseType.INCIDENT,
            status=SupportTicketStatus.OPEN,
            organization_id=data.organization_id,
            created_by=user_id,
            title=data.title,
            notes=data.notes,
        )
        ticket = await self._ticket_repo.add(ticket)

        if f.route_to_global:
            await self._auto_assign_global(ticket)
        else:
            await self._auto_assign_org(ticket)

        return await self._ticket_to_schema(ticket)

    async def escalate_ticket(self, ticket_number: int, f: SupportFilter) -> SupportTicketSchema:
        if not f.can_escalate:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para escalar tickets.")

        ticket = await self._ticket_repo.get_by_ticket_number(ticket_number)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        if ticket.status == SupportTicketStatus.RESOLVED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede escalar un ticket resuelto.")

        await self._auto_assign_global(ticket)
        return await self._ticket_to_schema(ticket)

    async def get_org_docs(self, ticket_number: int, f: SupportFilter) -> OrgDocsSchema:
        if not f.can_resolve:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        ticket = await self._ticket_repo.get_by_ticket_number(ticket_number)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        if ticket.case_type != SupportCaseType.REQUIREMENT:
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

    async def update_ticket_status(
        self, ticket_number: int, data: UpdateTicketStatusSchema, f: SupportFilter
    ) -> SupportTicketSchema:
        if not f.can_assign:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para mover tickets.")
        if data.status == SupportTicketStatus.RESOLVED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usa el endpoint de cierre para resolver tickets.")
        ticket = await self._ticket_repo.get_by_ticket_number(ticket_number)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        if ticket.status == SupportTicketStatus.RESOLVED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede mover un ticket resuelto.")
        ticket.status = data.status
        updated = await self._ticket_repo.update(ticket)
        return await self._ticket_to_schema(updated)

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

    async def _auto_assign_org(self, ticket: SupportTicketModel) -> None:
        agent_id = await self._ticket_repo.find_least_loaded_cs_org(ticket.organization_id)
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

    async def _auto_assign_global(self, ticket: SupportTicketModel) -> None:
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

    async def _ticket_to_schema(self, ticket: SupportTicketModel) -> SupportTicketSchema:
        org = await self._org_repo.get_by_id(ticket.organization_id)
        schema = SupportTicketSchema.model_validate(ticket)
        return schema.model_copy(update={"organization_name": org.name if org else ""})

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
