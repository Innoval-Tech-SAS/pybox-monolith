import uuid
from typing import Annotated

from fastapi import Query, status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global_admin, require_org_admin
from receivables.payment_gateways.dependencies import OrganizationGatewayCredentialManagementServiceDep
from receivables.payment_gateways.enums.payment_gateway_enums import ReceivablesGatewayProvider
from receivables.payment_gateways.schemas.payment_gateway_credential_schemas import (
    OrganizationGatewayCredentialCreateRequest,
    OrganizationGatewayCredentialResponse,
    OrganizationGatewayCredentialUpdateRequest,
)

router = APIRouter(prefix="/payment-gateway-credentials", tags=["Credenciales de Pasarela de la Organización"])

# Solo el ADMIN de la organización (o un admin global) puede ver/gestionar esto — a
# diferencia de payment_methods (que admite un permiso delegable), estas credenciales
# mueven dinero real de la empresa: no hay rol intermedio con acceso.


@router.get("/types", response_model=list[str], summary="Listar pasarelas soportadas")
async def list_provider_types(session: CurrentSession) -> list[str]:
    return [t.value for t in ReceivablesGatewayProvider]


@router.get("/", response_model=list[OrganizationGatewayCredentialResponse], summary="Listar credenciales de pasarela de la organización")
async def list_credentials(
    session: CurrentSession,
    service: OrganizationGatewayCredentialManagementServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> list[OrganizationGatewayCredentialResponse]:
    require_org_admin(session, str(organization_id))
    return await service.list(organization_id)


@router.get("/{id}", response_model=OrganizationGatewayCredentialResponse, summary="Obtener credencial de pasarela")
async def get_credential(
    id: uuid.UUID,
    session: CurrentSession,
    service: OrganizationGatewayCredentialManagementServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> OrganizationGatewayCredentialResponse:
    require_org_admin(session, str(organization_id))
    return await service.get(id, organization_id)


@router.post(
    "/",
    response_model=OrganizationGatewayCredentialResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar credencial de pasarela",
    description="Cifra los secretos enviados. Una organización solo puede tener una credencial activa por pasarela.",
)
async def create_credential(
    data: OrganizationGatewayCredentialCreateRequest,
    session: CurrentSession,
    service: OrganizationGatewayCredentialManagementServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> OrganizationGatewayCredentialResponse:
    require_org_admin(session, str(organization_id))
    return await service.create(organization_id, data)


@router.patch(
    "/{id}",
    response_model=OrganizationGatewayCredentialResponse,
    summary="Actualizar credencial de pasarela",
    description="Secretos vacíos conservan los existentes (rotar = enviar valor).",
)
async def update_credential(
    id: uuid.UUID,
    data: OrganizationGatewayCredentialUpdateRequest,
    session: CurrentSession,
    service: OrganizationGatewayCredentialManagementServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> OrganizationGatewayCredentialResponse:
    require_org_admin(session, str(organization_id))
    return await service.update(id, organization_id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar credencial de pasarela")
async def delete_credential(
    id: uuid.UUID,
    session: CurrentSession,
    service: OrganizationGatewayCredentialManagementServiceDep,
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
) -> None:
    require_org_admin(session, str(organization_id))
    await service.delete(id, organization_id)


@router.post(
    "/{id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationGatewayCredentialResponse,
    summary="Restaurar credencial de pasarela",
    description="Solo administradores globales.",
)
async def restore_credential(
    id: uuid.UUID,
    session: CurrentSession,
    service: OrganizationGatewayCredentialManagementServiceDep,
) -> OrganizationGatewayCredentialResponse:
    require_global_admin(session)
    return await service.restore(id)
