from config.api_router import APIRouter
from security.dependencies import CurrentSession
from users.dependencies import UserManagementServiceDep
from users.schemas.user_management_schemas import PermissionCatalogEntry

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("", response_model=list[PermissionCatalogEntry])
async def list_permissions_catalog(
    _session: CurrentSession,
    service: UserManagementServiceDep,
) -> list[PermissionCatalogEntry]:
    return await service.get_permissions_catalog()
