"""Endpoints de métodos de pago manuales configurados por la organización."""

import uuid
from typing import Annotated

from fastapi import Query, status

from core.config.api_router import APIRouter
from core.security.constants.permissions import ORG_PAYMENT_METHODS
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import (
    require_admin_or_org,
    require_global_admin,
)
from receivables.payment_methods.dependencies import PaymentMethodServiceDep
from receivables.payment_methods.enums.payment_method_enums import PaymentMethodType
from receivables.payment_methods.schemas.payment_method_schemas import (
    PaymentMethodCreateRequest,
    PaymentMethodResponse,
    PaymentMethodUpdateRequest,
)

router = APIRouter(prefix="/payment-methods", tags=["Métodos de pago"])


@router.get(
    "/types", response_model=list[str], summary="Listar tipos de método de pago"
)
async def list_payment_method_types(_session: CurrentSession) -> list[str]:
    return [t.value for t in PaymentMethodType]


@router.get(
    "/", response_model=list[PaymentMethodResponse], summary="Listar métodos de pago"
)
async def list_payment_methods(
    session: CurrentSession,
    service: PaymentMethodServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    is_active: Annotated[bool | None, Query(alias="isActive")] = None,
) -> list[PaymentMethodResponse]:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(organization_id))
    return await service.list(organization_id, is_active)


@router.get(
    "/{id}", response_model=PaymentMethodResponse, summary="Obtener método de pago"
)
async def get_payment_method(
    id: uuid.UUID,
    session: CurrentSession,
    service: PaymentMethodServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> PaymentMethodResponse:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(organization_id))
    return await service.get(id, organization_id)


@router.post(
    "/",
    response_model=PaymentMethodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear método de pago",
)
async def create_payment_method(
    data: PaymentMethodCreateRequest,
    session: CurrentSession,
    service: PaymentMethodServiceDep,
) -> PaymentMethodResponse:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(data.organization_id))
    return await service.create(data)


@router.patch(
    "/{id}", response_model=PaymentMethodResponse, summary="Actualizar método de pago"
)
async def update_payment_method(
    id: uuid.UUID,
    data: PaymentMethodUpdateRequest,
    session: CurrentSession,
    service: PaymentMethodServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> PaymentMethodResponse:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(organization_id))
    return await service.update(id, organization_id, data)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar método de pago"
)
async def delete_payment_method(
    id: uuid.UUID,
    session: CurrentSession,
    service: PaymentMethodServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> None:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(organization_id))
    await service.delete(id, organization_id)


@router.post(
    "/{id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=PaymentMethodResponse,
    summary="Restaurar método de pago",
    description="Solo administradores globales.",
)
async def restore_payment_method(
    id: uuid.UUID,
    session: CurrentSession,
    service: PaymentMethodServiceDep,
) -> PaymentMethodResponse:
    require_global_admin(session)
    return await service.restore(id)
