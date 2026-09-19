import uuid

from fastapi import status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global_admin
from app_platform.provider_credentials.dependencies import ProviderCredentialAdminServiceDep
from app_platform.provider_credentials.schemas.provider_credential_schemas import (
    ProviderCredentialResponse,
    ProviderCredentialUpsert,
)

router = APIRouter(prefix="/admin/provider-credentials", tags=["Credenciales de Proveedor (Admin)"])


@router.get(
    "",
    response_model=list[ProviderCredentialResponse],
    summary="Listar credenciales de proveedor",
    description="Lista todas las credenciales configuradas. Los secretos NO se devuelven descifrados. Solo ADMIN GLOBAL.",
)
async def list_credentials(
    session: CurrentSession,
    service: ProviderCredentialAdminServiceDep,
) -> list[ProviderCredentialResponse]:
    require_global_admin(session)
    return await service.list()


@router.put(
    "",
    response_model=ProviderCredentialResponse,
    summary="Crear o actualizar una credencial (upsert por país+proveedor)",
    description="Cifra los secretos enviados. Secretos vacíos conservan los existentes (rotar = enviar valor). Solo ADMIN GLOBAL.",
)
async def upsert_credential(
    body: ProviderCredentialUpsert,
    session: CurrentSession,
    service: ProviderCredentialAdminServiceDep,
) -> ProviderCredentialResponse:
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
    service: ProviderCredentialAdminServiceDep,
) -> None:
    require_global_admin(session)
    await service.delete(credential_id)


@router.post(
    "/{credential_id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=ProviderCredentialResponse,
    summary="Restaurar una credencial",
    description="Deshace la baja lógica de la credencial. Solo ADMIN GLOBAL.",
)
async def restore_credential(
    credential_id: uuid.UUID,
    session: CurrentSession,
    service: ProviderCredentialAdminServiceDep,
) -> ProviderCredentialResponse:
    require_global_admin(session)
    return await service.restore(credential_id)
