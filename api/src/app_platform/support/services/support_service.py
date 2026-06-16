import os
import re
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config.paths import UPLOADS_ROOT

from app_platform.notifications.services.notification_service import NotificationService
from identity.organizations.enums.organization_enums import VerificationStatus
from identity.organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from identity.organizations.repository.organization_repository import OrganizationRepository
from receivables.portfolios.repository.portfolio_user_access_repository import PortfolioUserAccessRepository
from app_platform.support.enums.support_enums import SupportCaseType, SupportTicketEventType, SupportTicketStatus
from app_platform.support.models.support_ticket_event_model import SupportTicketEventModel
from app_platform.support.models.support_ticket_message_model import SupportTicketMessageModel
from app_platform.support.models.support_ticket_model import SupportTicketModel
from app_platform.support.repository.support_event_repository import SupportEventRepository
from app_platform.support.repository.support_message_repository import SupportMessageRepository
from app_platform.support.repository.support_ticket_repository import SupportTicketRepository
from app_platform.support.schemas.support_schemas import AssignTicketSchema, CreateMessageSchema, CreateTicketSchema, OrgDocSchema, OrgDocsSchema, ResolveTicketSchema, SupportFilter, SupportTicketSchema, TicketAttachmentSchema, TicketCategorySchema, TicketEventSchema, TicketMessageSchema, TicketMetricsSchema, TicketOrgSchema, UpdateTicketPrioritySchema, UpdateTicketStatusSchema
from identity.users.schemas.user_session_schema import UserSession


class SupportService:
    def __init__(self, session: AsyncSession) -> None:
        self._ticket_repo = SupportTicketRepository(session)
        self._message_repo = SupportMessageRepository(session)
        self._event_repo = SupportEventRepository(session)
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
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f, check_creator=True)
        return await self._ticket_to_schema(ticket)

    async def resolve_ticket(
        self, ticket_number: int, agent_user_id: int, data: ResolveTicketSchema, f: SupportFilter
    ) -> SupportTicketSchema:
        if not f.can_resolve:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para resolver tickets.")
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f)
        if ticket.status == SupportTicketStatus.RESOLVED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El ticket ya fue resuelto.")

        prev_status = ticket.status
        ticket.status = SupportTicketStatus.RESOLVED
        ticket.assigned_to = agent_user_id
        ticket.notes = data.notes
        ticket.resolved_at = datetime.now(timezone.utc)

        await self._emit_event(
            ticket, agent_user_id, SupportTicketEventType.RESOLVED,
            from_value=prev_status.value, to_value=SupportTicketStatus.RESOLVED.value,
        )

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

    def get_categories(self) -> list[TicketCategorySchema]:
        return [
            TicketCategorySchema(label="Reportar un error", case_type=SupportCaseType.INCIDENT, description="Algo no funciona como se espera", icon="bug"),
            TicketCategorySchema(label="Nueva funcionalidad", case_type=SupportCaseType.INCIDENT, description="Propón una mejora o característica nueva", icon="sparkles"),
            TicketCategorySchema(label="Problema de acceso", case_type=SupportCaseType.INCIDENT, description="No puedo acceder a mi cuenta o a un módulo", icon="lock-keyhole"),
            TicketCategorySchema(label="Consulta general", case_type=SupportCaseType.INCIDENT, description="Tengo una pregunta sobre el sistema", icon="help-circle"),
            TicketCategorySchema(label="Validación de documentos", case_type=SupportCaseType.REQUIREMENT, description="Verificación documental de empresa", icon="file-check"),
            TicketCategorySchema(label="Otro", case_type=SupportCaseType.INCIDENT, description="Mi situación no encaja en las categorías anteriores", icon="more-horizontal"),
        ]

    async def get_ticket_orgs(self, session: UserSession) -> list[TicketOrgSchema]:
        if session.is_self:
            org_ids = await self._portfolio_access_repo.get_distinct_org_ids_by_user(session.user_id)
            result = []
            for org_id in org_ids:
                org = await self._org_repo.get_by_id(org_id)
                if org:
                    result.append(TicketOrgSchema(id=org.id, name=org.name))
            return result
        if session.orgs:
            return [
                TicketOrgSchema(id=uuid.UUID(org_id), name=entry.org_name)
                for org_id, entry in session.orgs.items()
            ]
        # Global scope (ADMIN GLOBAL / CS GLOBAL): return all orgs
        orgs = await self._org_repo.get_all()
        return [TicketOrgSchema(id=org.id, name=org.name) for org in orgs]

    async def create_ticket(self, user_id: int, data: CreateTicketSchema, f: SupportFilter) -> SupportTicketSchema:
        if not f.can_create:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para crear tickets.")

        # org_ids=None → GLOBAL scope: organización es opcional
        if f.org_ids is not None and data.organization_id is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La entidad es obligatoria.")

        if data.organization_id is not None:
            if f.check_portfolio_access:
                accesses = await self._portfolio_access_repo.get_active_by_user_and_org(user_id, data.organization_id)
                if not accesses:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta entidad.")
            elif f.org_ids is not None and data.organization_id not in f.org_ids:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes acceso a esta entidad.")

        ticket = SupportTicketModel(
            case_type=data.case_type,
            status=SupportTicketStatus.OPEN,
            priority=data.priority,
            organization_id=data.organization_id,
            created_by=user_id,
            title=data.title,
            notes=data.notes,
        )
        ticket = await self._ticket_repo.add(ticket)
        await self._emit_event(ticket, user_id, SupportTicketEventType.CREATED)
        await self._auto_assign(ticket, prefer_global=f.route_to_global)

        return await self._ticket_to_schema(ticket)

    async def escalate_ticket(self, ticket_number: int, f: SupportFilter) -> SupportTicketSchema:
        if not f.can_escalate:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para escalar tickets.")

        ticket = await self._get_ticket_or_404(ticket_number)
        if ticket.status == SupportTicketStatus.RESOLVED:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede escalar un ticket resuelto.")

        old_agent = ticket.assigned_to
        await self._auto_assign(ticket, prefer_global=True)
        if ticket.assigned_to and ticket.assigned_to != old_agent:
            await self._emit_event(
                ticket, ticket.assigned_to, SupportTicketEventType.ESCALATED,
                to_value=str(ticket.assigned_to),
            )
        return await self._ticket_to_schema(ticket)

    async def get_org_docs(self, ticket_number: int, f: SupportFilter) -> OrgDocsSchema:
        if not (f.can_resolve or f.can_assign):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        ticket = await self._get_ticket_or_404(ticket_number)
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

    _TERMINAL_STATUSES = {SupportTicketStatus.RESOLVED, SupportTicketStatus.CLOSED}

    async def update_ticket_status(
        self, ticket_number: int, user_id: int, data: UpdateTicketStatusSchema, f: SupportFilter
    ) -> SupportTicketSchema:
        if not f.can_assign:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para mover tickets.")
        if data.status in self._TERMINAL_STATUSES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usa el endpoint de cierre para resolver o cerrar tickets.")
        ticket = await self._get_ticket_or_404(ticket_number)
        if ticket.status in self._TERMINAL_STATUSES:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede mover un ticket resuelto o cerrado.")
        prev = ticket.status
        ticket.status = data.status
        updated = await self._ticket_repo.update(ticket)
        await self._emit_event(
            ticket, user_id, SupportTicketEventType.STATUS_CHANGED,
            from_value=prev.value, to_value=data.status.value,
        )
        return await self._ticket_to_schema(updated)

    async def update_ticket_priority(
        self, ticket_number: int, user_id: int, data: UpdateTicketPrioritySchema, f: SupportFilter
    ) -> SupportTicketSchema:
        if not f.can_assign:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para cambiar la prioridad.")
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f)
        prev = ticket.priority
        ticket.priority = data.priority
        updated = await self._ticket_repo.update(ticket)
        await self._emit_event(
            ticket, user_id, SupportTicketEventType.PRIORITY_CHANGED,
            from_value=prev.value, to_value=data.priority.value,
        )
        return await self._ticket_to_schema(updated)

    async def assign_ticket(
        self, ticket_number: int, actor_id: int, data: AssignTicketSchema, f: SupportFilter
    ) -> SupportTicketSchema:
        if not f.can_assign:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para asignar tickets.")
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f)
        if ticket.status in self._TERMINAL_STATUSES:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se puede reasignar un ticket resuelto o cerrado.")

        event_type = SupportTicketEventType.REASSIGNED if ticket.assigned_to else SupportTicketEventType.ASSIGNED
        prev_agent = str(ticket.assigned_to) if ticket.assigned_to else None
        ticket.assigned_to = data.user_id
        ticket.status = SupportTicketStatus.IN_PROGRESS
        updated = await self._ticket_repo.update(ticket)
        await self._emit_event(
            ticket, actor_id, event_type,
            from_value=prev_agent, to_value=str(data.user_id),
        )

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
    # Events (audit log)
    # ------------------------------------------------------------------

    async def list_events(self, ticket_number: int, f: SupportFilter) -> list[TicketEventSchema]:
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f, check_creator=True)
        events = await self._event_repo.get_by_ticket_id(ticket.id)
        return [TicketEventSchema.model_validate(e) for e in events]

    async def get_metrics(self, f: SupportFilter) -> TicketMetricsSchema:
        tickets = await self._ticket_repo.get_metrics_data(org_ids=f.org_ids)
        today = datetime.now(timezone.utc).date()

        by_priority: dict[str, int] = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
        _prio_map = {"Baja": "low", "Media": "medium", "Alta": "high", "Urgente": "urgent"}

        open_count = in_progress = pending = resolved = closed = 0
        created_today = resolved_today = 0
        resolution_hours: list[float] = []

        for t in tickets:
            s = t.status
            if s in (SupportTicketStatus.NEW, SupportTicketStatus.OPEN):
                open_count += 1
            elif s == SupportTicketStatus.IN_PROGRESS:
                in_progress += 1
            elif s in (SupportTicketStatus.PENDING_CLIENT, SupportTicketStatus.PENDING_THIRD):
                pending += 1
            elif s == SupportTicketStatus.RESOLVED:
                resolved += 1
                if t.resolved_at and t.resolved_at.date() == today:
                    resolved_today += 1
                if t.resolved_at and t.created_at:
                    delta = (t.resolved_at - t.created_at).total_seconds() / 3600
                    resolution_hours.append(delta)
            elif s == SupportTicketStatus.CLOSED:
                closed += 1

            if t.created_at.date() == today:
                created_today += 1

            prio_key = _prio_map.get(t.priority.value, "medium")
            by_priority[prio_key] = by_priority.get(prio_key, 0) + 1

        avg = round(sum(resolution_hours) / len(resolution_hours), 1) if resolution_hours else None

        return TicketMetricsSchema(
            total=len(tickets),
            open=open_count,
            in_progress=in_progress,
            pending=pending,
            resolved=resolved,
            closed=closed,
            created_today=created_today,
            resolved_today=resolved_today,
            avg_resolution_hours=avg,
            by_priority=by_priority,
        )

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    async def list_messages(
        self, ticket_number: int, f: SupportFilter
    ) -> list[TicketMessageSchema]:
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f, check_creator=True)
        messages = await self._message_repo.get_by_ticket_id(ticket.id)
        is_staff = f.can_resolve or f.can_assign
        return [
            TicketMessageSchema.model_validate(m)
            for m in messages
            if is_staff or not m.is_internal
        ]

    async def create_message(
        self,
        ticket_number: int,
        sender_id: int,
        data: CreateMessageSchema,
        f: SupportFilter,
    ) -> TicketMessageSchema:
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f, check_creator=True)
        if ticket.status in self._TERMINAL_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede enviar mensajes en un ticket cerrado.",
            )
        if data.is_internal and not (f.can_resolve or f.can_assign):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los agentes pueden enviar mensajes internos.",
            )

        message = await self._message_repo.add(
            SupportTicketMessageModel(
                ticket_id=ticket.id,
                sender_id=sender_id,
                body=data.body,
                is_internal=data.is_internal,
            )
        )

        await self._notify_new_message(ticket, sender_id, data.is_internal)
        return TicketMessageSchema.model_validate(message)

    async def _notify_new_message(
        self, ticket: SupportTicketModel, sender_id: int, is_internal: bool
    ) -> None:
        recipients: set[int] = set()
        if ticket.assigned_to and ticket.assigned_to != sender_id:
            recipients.add(ticket.assigned_to)
        if not is_internal and ticket.created_by != sender_id:
            recipients.add(ticket.created_by)

        for uid in recipients:
            await self._notification_service.create_notification(
                user_id=uid,
                title="Nuevo mensaje en ticket",
                body=f"Mensaje en ticket #{ticket.ticket_number}.",
                category="support_message",
                notif_type="info",
                link=f"/cs/tickets/{ticket.ticket_number}",
                details={"ticket_number": ticket.ticket_number},
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _emit_event(
        self,
        ticket: SupportTicketModel,
        user_id: int,
        event_type: SupportTicketEventType,
        from_value: str | None = None,
        to_value: str | None = None,
    ) -> None:
        await self._event_repo.add(
            SupportTicketEventModel(
                ticket_id=ticket.id,
                user_id=user_id,
                event_type=event_type,
                from_value=from_value,
                to_value=to_value,
            )
        )

    async def _get_ticket_or_404(self, ticket_number: int) -> SupportTicketModel:
        ticket = await self._ticket_repo.get_by_ticket_number(ticket_number)
        if ticket is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado.")
        return ticket

    def _assert_ticket_access(
        self,
        ticket: SupportTicketModel,
        f: "SupportFilter",
        *,
        check_creator: bool = False,
    ) -> None:
        if f.org_ids is not None and ticket.organization_id not in f.org_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        if check_creator and f.created_by is not None and ticket.created_by != f.created_by:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")

    _ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".doc"}
    _MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    @staticmethod
    def _safe_filename(name: str | None) -> str:
        if not name:
            return "attachment"
        safe = re.sub(r"[^\w.\-]", "_", name)
        return safe[:120]

    def _attachment_folder(self, ticket_number: int) -> str:
        return os.path.join(UPLOADS_ROOT, "tickets", str(ticket_number), "attachments")

    def _attachment_url(self, ticket_number: int, name: str) -> str:
        return f"/files/tickets/{ticket_number}/attachments/{name}"

    def _closure_folder(self, ticket_number: int) -> str:
        return os.path.join(UPLOADS_ROOT, "tickets", str(ticket_number), "closure")

    def _closure_url(self, ticket_number: int, name: str) -> str:
        return f"/files/tickets/{ticket_number}/closure/{name}"

    async def upload_attachments(
        self, ticket_number: int, files: list[UploadFile], f: SupportFilter
    ) -> list[TicketAttachmentSchema]:
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f, check_creator=True)

        folder = self._attachment_folder(ticket_number)
        os.makedirs(folder, exist_ok=True)

        result = []
        for upload in files:
            ext = os.path.splitext(upload.filename or "")[1].lower()
            if ext not in self._ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Tipo de archivo no permitido: {ext}")
            content = await upload.read()
            if len(content) > self._MAX_FILE_SIZE:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="El archivo excede el tamaño máximo de 10 MB.")
            safe_name = self._safe_filename(upload.filename)
            dest = os.path.join(folder, safe_name)
            with open(dest, "wb") as fh:
                fh.write(content)
            result.append(TicketAttachmentSchema(name=safe_name, url=self._attachment_url(ticket_number, safe_name), size=len(content)))
        return result

    async def upload_closure_attachments(
        self, ticket_number: int, files: list[UploadFile], f: SupportFilter
    ) -> list[TicketAttachmentSchema]:
        if not f.can_resolve:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para adjuntar evidencias de cierre.")
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f)

        folder = self._closure_folder(ticket_number)
        os.makedirs(folder, exist_ok=True)

        result = []
        for upload in files:
            ext = os.path.splitext(upload.filename or "")[1].lower()
            if ext not in self._ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Tipo de archivo no permitido: {ext}")
            content = await upload.read()
            if len(content) > self._MAX_FILE_SIZE:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="El archivo excede el tamaño máximo de 10 MB.")
            safe_name = self._safe_filename(upload.filename)
            dest = os.path.join(folder, safe_name)
            with open(dest, "wb") as fh:
                fh.write(content)
            result.append(TicketAttachmentSchema(name=safe_name, url=self._closure_url(ticket_number, safe_name), size=len(content)))
        return result

    async def list_closure_attachments(self, ticket_number: int, f: SupportFilter) -> list[TicketAttachmentSchema]:
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f, check_creator=True)

        folder = self._closure_folder(ticket_number)
        if not os.path.isdir(folder):
            return []
        result = []
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if os.path.isfile(path):
                result.append(TicketAttachmentSchema(name=name, url=self._closure_url(ticket_number, name), size=os.path.getsize(path)))
        return result

    async def list_attachments(self, ticket_number: int, f: SupportFilter) -> list[TicketAttachmentSchema]:
        ticket = await self._get_ticket_or_404(ticket_number)
        self._assert_ticket_access(ticket, f, check_creator=True)

        folder = self._attachment_folder(ticket_number)
        if not os.path.isdir(folder):
            return []
        result = []
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if os.path.isfile(path):
                result.append(TicketAttachmentSchema(name=name, url=self._attachment_url(ticket_number, name), size=os.path.getsize(path)))
        return result

    async def _auto_assign(
        self, ticket: SupportTicketModel, *, prefer_global: bool = False
    ) -> None:
        if prefer_global:
            agent_id = await self._ticket_repo.find_least_loaded_cs_global()
        else:
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

    async def _ticket_to_schema(self, ticket: SupportTicketModel) -> SupportTicketSchema:
        org_name = ""
        if ticket.organization_id is not None:
            org = await self._org_repo.get_by_id(ticket.organization_id)
            org_name = org.name if org else ""
        schema = SupportTicketSchema.model_validate(ticket)
        return schema.model_copy(update={"organization_name": org_name})

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
