from fastapi import APIRouter

from security.dependencies import CurrentSession
from support.dependencies import SupportAccessFilter, SupportServiceDep
from support.schemas.support_schemas import AssignTicketSchema, OrgDocsSchema, ResolveTicketSchema, SupportTicketSchema

router = APIRouter(prefix="/cs/tickets", tags=["Support"])


@router.get("", response_model=list[SupportTicketSchema])
async def list_tickets(f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_all_tickets(f)


@router.get("/{ticket_number}", response_model=SupportTicketSchema)
async def get_ticket(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_ticket(ticket_number, f)


@router.get("/{ticket_number}/org-docs", response_model=OrgDocsSchema)
async def get_org_docs(ticket_number: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_org_docs(ticket_number, f)


@router.post("/{ticket_number}/assign", response_model=SupportTicketSchema)
async def assign_ticket(
    ticket_number: int,
    body: AssignTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.assign_ticket(ticket_number, body, f)


@router.post("/{ticket_number}/resolve", response_model=SupportTicketSchema)
async def resolve_ticket(
    ticket_number: int,
    body: ResolveTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.resolve_ticket(ticket_number, session.user_id, body, f)
