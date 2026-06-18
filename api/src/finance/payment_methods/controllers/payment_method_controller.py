import uuid
from typing import Annotated

from fastapi import Query, status

from core.config.api_router import APIRouter
from finance.payment_methods.dependencies import PaymentMethodServiceDep
from finance.payment_methods.enums.payment_method_enums import PaymentMethodType
from finance.payment_methods.models.payment_method_model import PaymentMethodModel
from finance.payment_methods.schemas.payment_method_schemas import (
    PaymentMethodCreateRequest,
    PaymentMethodResponse,
    PaymentMethodUpdateRequest,
)
from core.security.dependencies import CurrentSession
from core.security.permissions import ORG_PAYMENT_METHODS
from core.security.policies import require_admin_or_org

router = APIRouter(prefix="/payment-methods", tags=["Métodos de pago"])


@router.get("/types", response_model=list[str], summary="Listar tipos de método de pago")
async def list_payment_method_types(session: CurrentSession) -> list[str]:
    return [t.value for t in PaymentMethodType]


@router.get("/", response_model=list[PaymentMethodResponse], summary="Listar métodos de pago")
async def list_payment_methods(
    session: CurrentSession,
    service: PaymentMethodServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    is_active: Annotated[bool | None, Query(alias="isActive")] = None,
) -> list[PaymentMethodModel]:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(organization_id))
    return await service.list(organization_id, is_active)


@router.get("/{id}", response_model=PaymentMethodResponse, summary="Obtener método de pago")
async def get_payment_method(
    id: int,
    session: CurrentSession,
    service: PaymentMethodServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> PaymentMethodModel:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(organization_id))
    return await service.get(id, organization_id)


@router.post("/", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED, summary="Crear método de pago")
async def create_payment_method(
    data: PaymentMethodCreateRequest,
    session: CurrentSession,
    service: PaymentMethodServiceDep,
) -> PaymentMethodModel:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(data.organization_id))
    return await service.create(data)


@router.patch("/{id}", response_model=PaymentMethodResponse, summary="Actualizar método de pago")
async def update_payment_method(
    id: int,
    data: PaymentMethodUpdateRequest,
    session: CurrentSession,
    service: PaymentMethodServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> PaymentMethodModel:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(organization_id))
    return await service.update(id, organization_id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar método de pago")
async def delete_payment_method(
    id: int,
    session: CurrentSession,
    service: PaymentMethodServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> None:
    require_admin_or_org(ORG_PAYMENT_METHODS, session, str(organization_id))
    await service.delete(id, organization_id)
