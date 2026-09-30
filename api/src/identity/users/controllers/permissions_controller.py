"""Endpoint de solo lectura del catálogo de permisos configurables."""

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from identity.users.dependencies import UserManagementServiceDep
from identity.users.schemas.user_management_schemas import PermissionCatalogEntry

router = APIRouter(prefix="/permissions", tags=["Permisos"])


@router.get(
    "",
    response_model=list[PermissionCatalogEntry],
    summary="Listar catálogo de permisos disponibles",
    description=(
        "Retorna todos los permisos configurables en el sistema con su nombre y "
        "descripción."
    ),
)
async def list_permissions_catalog(
    _session: CurrentSession,
    service: UserManagementServiceDep,
) -> list[PermissionCatalogEntry]:
    return await service.get_permissions_catalog()
