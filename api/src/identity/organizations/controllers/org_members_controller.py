import uuid

from fastapi import HTTPException, status

from core.config.api_router import APIRouter
from receivables.portfolios.dependencies import PortfolioUserAccessServiceDep
from core.security.dependencies import CurrentSession
from core.security.policies import require_org_admin
from identity.users.dependencies import UserManagementServiceDep
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.schemas.user_management_schemas import (
    ManagedUserCreate,
    ManagedUserResponse,
    PermissionAssignRequest,
    PermissionEntry,
    PermissionListResponse,
    PortfolioAccessEntry,
)

router = APIRouter(prefix="/organizations/{org_id}/members", tags=["Miembros de Organización"])


@router.post(
    "",
    response_model=ManagedUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear miembro de organización",
)
async def create_org_member(
    org_id: uuid.UUID,
    body: ManagedUserCreate,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> ManagedUserResponse:
    require_org_admin(session, str(org_id))
    if body.role not in {UserRole.ADMIN, UserRole.CUSTOMER_SERVICE, UserRole.USER_ORGANIZATION}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Rol inválido para miembros de organización.",
        )
    return await service.create_org_member(session.user_id, org_id, body)


@router.get(
    "/{user_id}/permissions",
    response_model=PermissionListResponse,
    summary="Listar permisos del miembro",
)
async def list_permissions(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> PermissionListResponse:
    require_org_admin(session, str(org_id))
    return await service.list_permissions(user_id, org_id)


@router.put(
    "/{user_id}/permissions",
    response_model=PermissionEntry,
    status_code=status.HTTP_200_OK,
    summary="Asignar permiso al miembro",
)
async def assign_permission(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    body: PermissionAssignRequest,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> PermissionEntry:
    require_org_admin(session, str(org_id))
    return await service.assign_permission(user_id, org_id, body.name, body.effect)


@router.delete(
    "/{user_id}/permissions/{permission_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revocar permiso del miembro",
)
async def remove_permission(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    permission_name: str,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> None:
    require_org_admin(session, str(org_id))
    await service.remove_permission(user_id, org_id, permission_name)


@router.get(
    "/{user_id}/portfolios",
    response_model=list[PortfolioAccessEntry],
    summary="Listar portafolios con acceso del miembro",
)
async def list_portfolio_access(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    session: CurrentSession,
    access_service: PortfolioUserAccessServiceDep,
) -> list[PortfolioAccessEntry]:
    require_org_admin(session, str(org_id))
    items = await access_service.list_org_portfolios_with_access_status(user_id, org_id)
    return [PortfolioAccessEntry(portfolio_id=pid, name=name, has_access=has) for pid, name, has in items]


@router.put(
    "/{user_id}/portfolios/{portfolio_id}",
    status_code=status.HTTP_200_OK,
    summary="Conceder acceso a portafolio",
)
async def grant_portfolio_access(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    portfolio_id: uuid.UUID,
    session: CurrentSession,
    access_service: PortfolioUserAccessServiceDep,
) -> None:
    require_org_admin(session, str(org_id))
    await access_service.grant_access(user_id, portfolio_id, org_id, granted_by=session.user_id)


@router.delete(
    "/{user_id}/portfolios/{portfolio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revocar acceso a portafolio",
)
async def revoke_portfolio_access(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    portfolio_id: uuid.UUID,
    session: CurrentSession,
    access_service: PortfolioUserAccessServiceDep,
) -> None:
    require_org_admin(session, str(org_id))
    await access_service.revoke_access(user_id, portfolio_id)
