from fastapi import APIRouter

from security.dependencies import CurrentSession
from support.dependencies import SupportAccessFilter, SupportServiceDep
from support.schemas.support_schemas import AssignTicketSchema, ResolveTicketSchema, SupportTicketSchema

router = APIRouter(prefix="/cs/tickets", tags=["Support"])


@router.get("", response_model=list[SupportTicketSchema])
async def list_tickets(f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_all_tickets(f)


@router.get("/{ticket_id}", response_model=SupportTicketSchema)
async def get_ticket(ticket_id: int, f: SupportAccessFilter, service: SupportServiceDep):
    return await service.get_ticket(ticket_id, f)


@router.post("/{ticket_id}/assign", response_model=SupportTicketSchema)
async def assign_ticket(
    ticket_id: int,
    body: AssignTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
):
    return await service.assign_ticket(ticket_id, body, f)


@router.post("/{ticket_id}/resolve", response_model=SupportTicketSchema)
async def resolve_ticket(
    ticket_id: int,
    body: ResolveTicketSchema,
    f: SupportAccessFilter,
    service: SupportServiceDep,
    session: CurrentSession,
):
    return await service.resolve_ticket(ticket_id, session.user_id, body, f)
