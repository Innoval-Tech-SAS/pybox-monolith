import uuid

from fastapi import HTTPException, status

from config.api_router import APIRouter
from security.dependencies import CurrentSession
from users.dependencies import UserManagementServiceDep
from users.enums.user_enums import UserRole, UserScope
from users.schemas.user_management_schemas import (
    ManagedUserCreate,
    ManagedUserResponse,
    PermissionAssignRequest,
    PermissionEntry,
    PermissionListResponse,
)

router = APIRouter(prefix="/organizations/{org_id}/members", tags=["org-members"])


def _require_org_admin(session: CurrentSession, org_id: uuid.UUID) -> int:
    if session.scope != UserScope.ORGANIZATION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
    org_entry = session.orgs.get(str(org_id))
    if org_entry is None or org_entry.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a administradores de la organización.")
    return session.user_id


@router.post("", response_model=ManagedUserResponse, status_code=status.HTTP_201_CREATED)
async def create_org_member(
    org_id: uuid.UUID,
    body: ManagedUserCreate,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> ManagedUserResponse:
    actor_id = _require_org_admin(session, org_id)
    if body.role not in {UserRole.ADMIN, UserRole.CUSTOMER_SERVICE, UserRole.USER_ORGANIZATION}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Rol inválido para miembros de organización.",
        )
    return await service.create_org_member(actor_id, org_id, body)


@router.get("/{user_id}/permissions", response_model=PermissionListResponse)
async def list_permissions(
    org_id: uuid.UUID,
    user_id: int,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> PermissionListResponse:
    _require_org_admin(session, org_id)
    return await service.list_permissions(user_id, org_id)


@router.put("/{user_id}/permissions", response_model=PermissionEntry, status_code=status.HTTP_200_OK)
async def assign_permission(
    org_id: uuid.UUID,
    user_id: int,
    body: PermissionAssignRequest,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> PermissionEntry:
    _require_org_admin(session, org_id)
    return await service.assign_permission(user_id, org_id, body.name, body.effect)


@router.delete("/{user_id}/permissions/{permission_name}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permission(
    org_id: uuid.UUID,
    user_id: int,
    permission_name: str,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> None:
    _require_org_admin(session, org_id)
    await service.remove_permission(user_id, org_id, permission_name)
