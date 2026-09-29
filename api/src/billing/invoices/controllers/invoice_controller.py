import uuid
from typing import Annotated

from fastapi import HTTPException, Query, status

from billing.invoices.dependencies import InvoiceServiceDep
from billing.invoices.schemas.invoice_schemas import (
    AdminInvoiceResponse,
    AdminListInvoicesResponse,
    CurrentInvoiceResponse,
    InvoiceResponse,
    ListInvoicesResponse,
    MercadoPagoChargeRequest,
    PaymentLinkResponse,
)
from core.config.api_router import APIRouter
from core.security.constants.permissions import ORG_BILLING
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global, require_permission
from identity.users.schemas.user_session_schema import UserSession

router = APIRouter(prefix="/billing", tags=["Facturación"])

OrganizationIdQuery = Annotated[uuid.UUID, Query(alias="organizationId")]


def _require_billing_payer(session: UserSession, organization_id: str) -> None:
    """Los administradores globales solo consultan la facturacion; no pagan."""
    if session.is_global:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Los administradores globales no pueden realizar pagos, solo "
            "consultar la facturación.",
        )
    require_permission(ORG_BILLING, session, organization_id)


@router.get(
    "/current-invoice",
    response_model=CurrentInvoiceResponse,
    summary="Obtener factura vigente",
)
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
    summary="Crear o reutilizar el enlace de pago",
)
async def create_or_reuse_payment_link(
    id: uuid.UUID,
    session: CurrentSession,
    service: InvoiceServiceDep,
    organization_id: OrganizationIdQuery,
) -> PaymentLinkResponse:
    _require_billing_payer(session, str(organization_id))
    return await service.create_or_reuse_payment_link(
        id, organization_id, session.email
    )


@router.post(
    "/invoices/{id}/attempts/{attempt_id}/mercadopago/charge",
    response_model=InvoiceResponse,
    summary="Cobrar un intento de pago de Mercado Pago (Orders API, modo manual)",
)
async def charge_mercadopago_attempt(
    id: uuid.UUID,
    attempt_id: uuid.UUID,
    body: MercadoPagoChargeRequest,
    session: CurrentSession,
    service: InvoiceServiceDep,
    organization_id: OrganizationIdQuery,
) -> InvoiceResponse:
    _require_billing_payer(session, str(organization_id))
    return await service.charge_mercadopago_attempt(  # type: ignore[return-value]
        id,
        organization_id,
        attempt_id,
        body.token,
        body.payment_method_id,
        body.payment_type_id,
        body.installments,
    )


@router.post(
    "/invoices/{id}/sync",
    response_model=InvoiceResponse,
    summary="Sincronizar estado de pago",
)
async def sync_invoice_payment_status(
    id: uuid.UUID,
    session: CurrentSession,
    service: InvoiceServiceDep,
    organization_id: OrganizationIdQuery,
) -> InvoiceResponse:
    _require_billing_payer(session, str(organization_id))
    return await service.sync_invoice_payment_status(  # type: ignore[return-value]
        id, organization_id
    )


@router.get(
    "/admin/invoices",
    response_model=AdminListInvoicesResponse,
    summary="Listar facturas de todas las organizaciones (solo admin global)",
)
async def list_invoices_admin(
    session: CurrentSession,
    service: InvoiceServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    organization_id: Annotated[uuid.UUID | None, Query(alias="organizationId")] = None,
) -> AdminListInvoicesResponse:
    require_global(session)
    return await service.list_invoices_admin(page, limit, organization_id)


@router.get(
    "/admin/invoices/{id}",
    response_model=AdminInvoiceResponse,
    summary="Obtener cualquier factura de cualquier organizacion (solo admin global)",
)
async def get_invoice_admin(
    id: uuid.UUID,
    session: CurrentSession,
    service: InvoiceServiceDep,
) -> AdminInvoiceResponse:
    require_global(session)
    return await service.get_invoice_admin(id)
