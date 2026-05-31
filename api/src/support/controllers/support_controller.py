from typing import Annotated
from fastapi import APIRouter, File, UploadFile

from security.dependencies import CurrentSession
from support.dependencies import SupportAccessFilter, SupportServiceDep
from support.schemas.support_schemas import AssignTicketSchema, CreateMessageSchema, CreateTicketSchema, OrgDocsSchema, ResolveTicketSchema, SupportTicketSchema, TicketAttachmentSchema, TicketCategorySchema, TicketEventSchema, TicketMessageSchema, TicketMetricsSchema, TicketOrgSchema, UpdateTicketPrioritySchema, UpdateTicketStatusSchema

router = APIRouter(prefix="/cs/tickets", tags=["Soporte"])


@router.get("/metrics", response_model=TicketMetricsSchema, summary="Métricas de tickets")
async def get_metrics(f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_metrics(f)


@router.get("/categories", response_model=list[TicketCategorySchema], summary="Listar categorías de tickets")
async def get_ticket_categories(service: SupportServiceDep):
    return service.get_categories()


@router.get("/orgs", response_model=list[TicketOrgSchema], summary="Listar organizaciones con tickets")
async def get_ticket_orgs(session: CurrentSession, service: SupportServiceDep):
    return await service.get_ticket_orgs(session)


@router.get("", response_model=list[SupportTicketSchema], summary="Listar tickets de soporte")
async def list_tickets(f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_all_tickets(f)


@router.post("", response_model=SupportTicketSchema, status_code=201, summary="Crear ticket de soporte")
async def create_ticket(
    body: CreateTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.create_ticket(session.user_id, body, f)


@router.get("/{ticket_number}", response_model=SupportTicketSchema, summary="Obtener ticket por número")
async def get_ticket(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_ticket(ticket_number, f)


@router.get(
    "/{ticket_number}/org-docs",
    response_model=OrgDocsSchema,
    summary="Obtener documentos de la organización del ticket",
)
async def get_org_docs(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_org_docs(ticket_number, f)


@router.patch(
    "/{ticket_number}/status",
    response_model=SupportTicketSchema,
    summary="Actualizar estado del ticket",
)
async def update_ticket_status(
    ticket_number: int,
    body: UpdateTicketStatusSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.update_ticket_status(ticket_number, session.user_id, body, f)


@router.post(
    "/{ticket_number}/assign",
    response_model=SupportTicketSchema,
    summary="Asignar ticket a un agente",
)
async def assign_ticket(
    ticket_number: int,
    body: AssignTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.assign_ticket(ticket_number, session.user_id, body, f)


@router.get(
    "/{ticket_number}/attachments",
    response_model=list[TicketAttachmentSchema],
    summary="Listar adjuntos del ticket",
)
async def list_attachments(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.list_attachments(ticket_number, f)


@router.post(
    "/{ticket_number}/attachments",
    response_model=list[TicketAttachmentSchema],
    summary="Subir adjuntos al ticket",
)
async def upload_attachments(
    ticket_number: int,
    files: Annotated[list[UploadFile], File()],
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.upload_attachments(ticket_number, files, f)


@router.get(
    "/{ticket_number}/closure-attachments",
    response_model=list[TicketAttachmentSchema],
    summary="Listar adjuntos de cierre del ticket",
)
async def list_closure_attachments(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.list_closure_attachments(ticket_number, f)


@router.post(
    "/{ticket_number}/closure-attachments",
    response_model=list[TicketAttachmentSchema],
    summary="Subir adjuntos de cierre del ticket",
)
async def upload_closure_attachments(
    ticket_number: int,
    files: Annotated[list[UploadFile], File()],
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.upload_closure_attachments(ticket_number, files, f)


@router.get(
    "/{ticket_number}/messages",
    response_model=list[TicketMessageSchema],
    summary="Listar mensajes del ticket",
)
async def list_messages(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.list_messages(ticket_number, f)


@router.post(
    "/{ticket_number}/messages",
    response_model=TicketMessageSchema,
    status_code=201,
    summary="Enviar mensaje al ticket",
)
async def create_message(
    ticket_number: int,
    body: CreateMessageSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.create_message(ticket_number, session.user_id, body, f)


@router.get(
    "/{ticket_number}/events",
    response_model=list[TicketEventSchema],
    summary="Historial de cambios del ticket",
)
async def list_events(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.list_events(ticket_number, f)


@router.patch(
    "/{ticket_number}/priority",
    response_model=SupportTicketSchema,
    summary="Cambiar prioridad del ticket",
)
async def update_ticket_priority(
    ticket_number: int,
    body: UpdateTicketPrioritySchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.update_ticket_priority(ticket_number, session.user_id, body, f)


@router.post(
    "/{ticket_number}/escalate",
    response_model=SupportTicketSchema,
    summary="Escalar ticket a nivel superior",
)
async def escalate_ticket(
    ticket_number: int,
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.escalate_ticket(ticket_number, f)


@router.post(
    "/{ticket_number}/resolve",
    response_model=SupportTicketSchema,
    summary="Resolver ticket de soporte",
)
async def resolve_ticket(
    ticket_number: int,
    body: ResolveTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.resolve_ticket(ticket_number, session.user_id, body, f)
