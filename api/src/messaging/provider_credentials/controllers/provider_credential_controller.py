import uuid

from fastapi import status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global_admin
from messaging.provider_credentials.dependencies import MessagingProviderCredentialAdminServiceDep
from messaging.provider_credentials.schemas.provider_credential_schemas import (
    MessagingProviderCredentialResponse,
    MessagingProviderCredentialUpsert,
)

router = APIRouter(prefix="/admin/messaging-credentials", tags=["Credenciales de Mensajería (Admin)"])


@router.get(
    "",
    response_model=list[MessagingProviderCredentialResponse],
    summary="Listar credenciales de mensajería",
    description="Lista todas las credenciales configuradas. Los secretos NO se devuelven descifrados. Solo ADMIN GLOBAL.",
)
async def list_credentials(
    session: CurrentSession,
    service: MessagingProviderCredentialAdminServiceDep,
) -> list[MessagingProviderCredentialResponse]:
    require_global_admin(session)
    return await service.list()


@router.put(
    "",
    response_model=MessagingProviderCredentialResponse,
    summary="Crear o actualizar una credencial (upsert por país+proveedor)",
    description="Cifra los secretos enviados. Secretos vacíos conservan los existentes (rotar = enviar valor). Solo ADMIN GLOBAL.",
)
async def upsert_credential(
    body: MessagingProviderCredentialUpsert,
    session: CurrentSession,
    service: MessagingProviderCredentialAdminServiceDep,
) -> MessagingProviderCredentialResponse:
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
    service: MessagingProviderCredentialAdminServiceDep,
) -> None:
    require_global_admin(session)
    await service.delete(credential_id)


@router.post(
    "/{credential_id}/restore",
    status_code=status.HTTP_200_OK,
    response_model=MessagingProviderCredentialResponse,
    summary="Restaurar una credencial",
    description="Deshace la baja lógica de la credencial. Solo ADMIN GLOBAL.",
)
async def restore_credential(
    credential_id: uuid.UUID,
    session: CurrentSession,
    service: MessagingProviderCredentialAdminServiceDep,
) -> MessagingProviderCredentialResponse:
    require_global_admin(session)
    return await service.restore(credential_id)
