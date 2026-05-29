from typing import Annotated
from fastapi import APIRouter, File, UploadFile

from security.dependencies import CurrentSession
from support.dependencies import SupportAccessFilter, SupportServiceDep
from support.schemas.support_schemas import AssignTicketSchema, CreateTicketSchema, OrgDocsSchema, ResolveTicketSchema, SupportTicketSchema, TicketAttachmentSchema, TicketCategorySchema, TicketOrgSchema, UpdateTicketStatusSchema

router = APIRouter(prefix="/cs/tickets", tags=["Support"])


@router.get("/categories", response_model=list[TicketCategorySchema])
async def get_ticket_categories(service: SupportServiceDep):
    return service.get_categories()


@router.get("/orgs", response_model=list[TicketOrgSchema])
async def get_ticket_orgs(session: CurrentSession, service: SupportServiceDep):
    return await service.get_ticket_orgs(session)


@router.get("", response_model=list[SupportTicketSchema])
async def list_tickets(f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_all_tickets(f)


@router.post("", response_model=SupportTicketSchema, status_code=201)
async def create_ticket(
    body: CreateTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.create_ticket(session.user_id, body, f)


@router.get("/{ticket_number}", response_model=SupportTicketSchema)
async def get_ticket(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_ticket(ticket_number, f)


@router.get("/{ticket_number}/org-docs", response_model=OrgDocsSchema)
async def get_org_docs(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_org_docs(ticket_number, f)


@router.patch("/{ticket_number}/status", response_model=SupportTicketSchema)
async def update_ticket_status(
    ticket_number: int,
    body: UpdateTicketStatusSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.update_ticket_status(ticket_number, body, f)


@router.post("/{ticket_number}/assign", response_model=SupportTicketSchema)
async def assign_ticket(
    ticket_number: int,
    body: AssignTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.assign_ticket(ticket_number, body, f)


@router.get("/{ticket_number}/attachments", response_model=list[TicketAttachmentSchema])
async def list_attachments(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.list_attachments(ticket_number, f)


@router.post("/{ticket_number}/attachments", response_model=list[TicketAttachmentSchema])
async def upload_attachments(
    ticket_number: int,
    files: Annotated[list[UploadFile], File()],
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.upload_attachments(ticket_number, files, f)


@router.get("/{ticket_number}/closure-attachments", response_model=list[TicketAttachmentSchema])
async def list_closure_attachments(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.list_closure_attachments(ticket_number, f)


@router.post("/{ticket_number}/closure-attachments", response_model=list[TicketAttachmentSchema])
async def upload_closure_attachments(
    ticket_number: int,
    files: Annotated[list[UploadFile], File()],
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.upload_closure_attachments(ticket_number, files, f)


@router.post("/{ticket_number}/escalate", response_model=SupportTicketSchema)
async def escalate_ticket(
    ticket_number: int,
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.escalate_ticket(ticket_number, f)


@router.post("/{ticket_number}/resolve", response_model=SupportTicketSchema)
async def resolve_ticket(
    ticket_number: int,
    body: ResolveTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.resolve_ticket(ticket_number, session.user_id, body, f)
