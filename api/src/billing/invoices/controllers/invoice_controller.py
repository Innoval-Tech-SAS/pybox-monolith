import uuid
from typing import Annotated

from fastapi import Query

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.permissions import ORG_BILLING
from core.security.policies import require_permission
from billing.invoices.dependencies import InvoiceServiceDep
from billing.invoices.schemas.invoice_schemas import (
    CurrentInvoiceResponse,
    InvoiceResponse,
    ListInvoicesResponse,
    PaymentLinkResponse,
)

router = APIRouter(prefix="/billing", tags=["Facturación"])

OrganizationIdQuery = Annotated[uuid.UUID, Query(alias="organizationId")]


@router.get("/current-invoice", response_model=CurrentInvoiceResponse, summary="Obtener factura vigente")
async def get_current_invoice(
    session: CurrentSession,
    service: InvoiceServiceDep,
    organization_id: OrganizationIdQuery,
) -> CurrentInvoiceResponse:
    require_permission(ORG_BILLING, session, str(organization_id))
    invoice = await service.get_current_invoice(organization_id)
    return CurrentInvoiceResponse(invoice=invoice)  # type: ignore[arg-type]


@router.get("/invoices", response_model=ListInvoicesResponse, summary="Listar facturas")
async def list_invoices(
    session: CurrentSession,
    service: InvoiceServiceDep,
    organization_id: OrganizationIdQuery,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> ListInvoicesResponse:
    require_permission(ORG_BILLING, session, str(organization_id))
    return await service.list_invoices(organization_id, page, limit)


@router.get("/invoices/{id}", response_model=InvoiceResponse, summary="Obtener factura")
async def get_invoice(
    id: uuid.UUID,
    session: CurrentSession,
    service: InvoiceServiceDep,
    organization_id: OrganizationIdQuery,
) -> InvoiceResponse:
    require_permission(ORG_BILLING, session, str(organization_id))
    return await service.get_invoice(id, organization_id)  # type: ignore[return-value]


@router.post(
    "/invoices/{id}/payment-link",
    response_model=PaymentLinkResponse,
    summary="Crear o reutilizar el enlace de pago Bold",
)
async def create_or_reuse_payment_link(
    id: uuid.UUID,
    session: CurrentSession,
    service: InvoiceServiceDep,
    organization_id: OrganizationIdQuery,
) -> PaymentLinkResponse:
    require_permission(ORG_BILLING, session, str(organization_id))
    return await service.create_or_reuse_payment_link(id, organization_id)


@router.post("/invoices/{id}/sync", response_model=InvoiceResponse, summary="Sincronizar estado de pago")
async def sync_invoice_payment_status(
    id: uuid.UUID,
    session: CurrentSession,
    service: InvoiceServiceDep,
    organization_id: OrganizationIdQuery,
) -> InvoiceResponse:
    require_permission(ORG_BILLING, session, str(organization_id))
    return await service.sync_invoice_payment_status(id, organization_id)  # type: ignore[return-value]
