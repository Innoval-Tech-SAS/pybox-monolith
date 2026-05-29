from fastapi import HTTPException, status

from config.api_router import APIRouter
from security.dependencies import CurrentSession
from users.dependencies import UserManagementServiceDep
from users.enums.user_enums import UserRole, UserScope
from users.schemas.user_management_schemas import GlobalAdminCreate, ManagedUserCreate, ManagedUserResponse

router = APIRouter(prefix="/users/global", tags=["Usuarios Globales"])


def _require_global_admin(session: CurrentSession) -> None:
    if not session.is_global or session.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a administradores globales.")


@router.post(
    "",
    response_model=ManagedUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario global",
    description="Crea un usuario con scope global (ADMIN o CUSTOMER_SERVICE). Solo administradores globales.",
)
async def create_global_user(
    body: ManagedUserCreate,
    session: CurrentSession,
    service: UserManagementServiceDep,
) -> ManagedUserResponse:
    _require_global_admin(session)
    if body.role not in {UserRole.ADMIN, UserRole.CUSTOMER_SERVICE}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Rol inválido. Permitidos para usuarios globales: {UserRole.ADMIN.value}, {UserRole.CUSTOMER_SERVICE.value}",
        )
    return await service.create_global_user(body)


@router.post(
    "/admin",
    response_model=ManagedUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear administrador global (bootstrap)",
    description="Crea el primer administrador global del sistema. Uso exclusivo en inicialización.",
)
async def create_global_admin(
    body: GlobalAdminCreate,
    service: UserManagementServiceDep,
) -> ManagedUserResponse:
    data = ManagedUserCreate(**body.model_dump(), role=UserRole.ADMIN)
    return await service.create_global_user(data)
