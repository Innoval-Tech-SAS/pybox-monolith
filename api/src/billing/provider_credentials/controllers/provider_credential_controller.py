import uuid

from fastapi import status

from billing.provider_credentials.dependencies import (
    PlatformGatewayCredentialAdminServiceDep,
)
from billing.provider_credentials.schemas.provider_credential_schemas import (
    PlatformGatewayCredentialResponse,
    PlatformGatewayCredentialUpsert,
)
from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global_admin

router = APIRouter(
    prefix="/admin/platform-gateway-credentials",
    tags=["Credenciales de Pasarela de Plataforma (Admin)"],
)


@router.get(
    "",
    response_model=list[PlatformGatewayCredentialResponse],
    summary="Listar credenciales de pasarela de la plataforma",
    description=(
        "Lista todas las credenciales configuradas. Los secretos NO se devuelven "
        "descifrados. Solo ADMIN GLOBAL."
    ),
)
async def list_credentials(
    session: CurrentSession,
    service: PlatformGatewayCredentialAdminServiceDep,
) -> list[PlatformGatewayCredentialResponse]:
    require_global_admin(session)
    return await service.list()


@router.put(
    "",
    response_model=PlatformGatewayCredentialResponse,
    summary="Crear o actualizar una credencial (upsert por país+proveedor)",
    description=(
        "Cifra los secretos enviados. Secretos vacíos conservan los existentes "
        "(rotar = enviar valor). Solo ADMIN GLOBAL."
    ),
)
async def upsert_credential(
    body: PlatformGatewayCredentialUpsert,
    session: CurrentSession,
    service: PlatformGatewayCredentialAdminServiceDep,
) -> PlatformGatewayCredentialResponse:
    require_global_admin(session)
    return await service.upsert(body)


@router.delete(
    "/{credential_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una credencial",
    description="Elimina la credencial por id. Solo ADMIN GLOBAL.",
)
async def delete_credential(
    credential_id: uuid.UUID,
    session: CurrentSession,
    service: PlatformGatewayCredentialAdminServiceDep,
) -> None:
    require_global_admin(session)
    await service.delete(credential_id)


@router.post(
    "/{credential_id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=PlatformGatewayCredentialResponse,
    summary="Restaurar una credencial",
    description="Deshace la baja lógica de la credencial. Solo ADMIN GLOBAL.",
)
async def restore_credential(
    credential_id: uuid.UUID,
    session: CurrentSession,
    service: PlatformGatewayCredentialAdminServiceDep,
) -> PlatformGatewayCredentialResponse:
    require_global_admin(session)
    return await service.restore(credential_id)
