"""Endpoints de gestión de administradores globales de la plataforma."""

from fastapi import HTTPException, status

from core.config.api_router import APIRouter
from core.security.dependencies import CurrentSession
from core.security.policies.security_policies import require_global_admin
from identity.users.dependencies import UserManagementServiceDep
from identity.users.enums.user_enums import UserRole
from identity.users.schemas.user_management_schemas import (
    GlobalAdminCreate,
    ManagedUserCreate,
    ManagedUserResponse,
)

router = APIRouter(prefix="/users/global", tags=["Usuarios Globales"])


@router.post(
    "",
    response_model=ManagedUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario global",
    description=(
        "Crea un usuario con scope global (ADMIN o CUSTOMER_SERVICE). Solo "
        "administradores globales."
    ),
)
async def create_global_user(
    body: ManagedUserCreate,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> ManagedUserResponse:
    require_global_admin(session)
    if body.role not in {UserRole.ADMIN, UserRole.CUSTOMER_SERVICE}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Rol inválido. Permitidos para usuarios globales: "
                f"{UserRole.ADMIN.value}, {UserRole.CUSTOMER_SERVICE.value}"
            ),
        )
    return await service.create_global_user(body)


@router.post(
    "/admin",
    response_model=ManagedUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear administrador global",
    description=(
        "Crea un administrador global adicional. Solo administradores globales."
    ),
)
async def create_global_admin(
    body: GlobalAdminCreate,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> ManagedUserResponse:
    require_global_admin(session)
    data = ManagedUserCreate(**body.model_dump(), role=UserRole.ADMIN)
    return await service.create_global_user(data)
