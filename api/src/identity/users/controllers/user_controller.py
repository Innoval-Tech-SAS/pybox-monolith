import uuid

from core.config.api_router import APIRouter
from fastapi import File, HTTPException, Query, UploadFile, status
from pydantic import ValidationError as PydanticValidationError

from identity.auth.dependencies import TokenPayload
from core.security.dependencies import CurrentSession
from core.security.permissions import ORG_USERS
from core.security.policies import require_admin_or_org
from identity.users.dependencies import UserServiceDep
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.schemas.user_preferences_schema import UserToursSchema
from identity.users.schemas.user_schemas import AdminUserDetailSchema, AdminUserSummarySchema, ChatAvailableUserSchema, ProfilePhotoSchema, UpdateUserSchema
from identity.users.schemas.user_session_schema import UserSession, session_key

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/me", response_model=UserSession, summary="Obtener sesión del usuario autenticado")
async def me(payload: TokenPayload, service: UserServiceDep) -> UserSession:
    try:
        user_id = uuid.UUID(str(payload["sub"]))
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

    try:
        cached = await service.redis.get_json(session_key(user_id), UserSession)
    except PydanticValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tu sesión no es válida. Inicia sesión nuevamente.",
        )
    if cached is not None:
        return cached
    return await service.get_user_session(user_id)


@router.get(
    "/me/preferences/tours",
    response_model=UserToursSchema,
    summary="Obtener tours descartados por el usuario",
)
async def get_tour_preferences(payload: TokenPayload, service: UserServiceDep) -> UserToursSchema:
    user_id = uuid.UUID(str(payload["sub"]))
    dismissed = await service.get_dismissed_tours(user_id)
    return UserToursSchema(dismissed_tours=dismissed)


@router.post(
    "/me/preferences/tours/{tour_key}/dismiss",
    response_model=UserToursSchema,
    summary="Descartar un tour de la interfaz",
)
async def dismiss_tour(tour_key: str, payload: TokenPayload, service: UserServiceDep) -> UserToursSchema:
    user_id = uuid.UUID(str(payload["sub"]))
    dismissed = await service.dismiss_tour(user_id, tour_key)
    return UserToursSchema(dismissed_tours=dismissed)


@router.put(
    "/me/profile-photo",
    response_model=ProfilePhotoSchema,
    summary="Actualizar foto de perfil",
)
async def update_profile_photo(
    payload: TokenPayload,
    service: UserServiceDep,
    file: UploadFile = File(...),
) -> ProfilePhotoSchema:
    user_id = uuid.UUID(str(payload["sub"]))
    return await service.update_profile_photo(user_id, file)


@router.get(
    "/available-for-chat",
    response_model=list[ChatAvailableUserSchema],
    summary="Listar usuarios disponibles para chat",
)
async def get_available_for_chat(session: CurrentSession, service: UserServiceDep):
    return await service.get_available_for_chat(session)


@router.get(
    "",
    response_model=list[AdminUserSummarySchema],
    summary="Listar usuarios",
    description="Lista los usuarios accesibles según el rol del solicitante. Soporta filtro por organización.",
)
async def list_users(session: CurrentSession, service: UserServiceDep, org_id: str | None = Query(None)):
    if session.is_global:
        org_ids = [uuid.UUID(org_id)] if org_id else None
        return await service.get_accessible_users(org_ids=org_ids)

    if session.scope != UserScope.ORGANIZATION:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")

    if org_id:
        require_admin_or_org(ORG_USERS, session, org_id)
        org_ids = [uuid.UUID(org_id)]
    else:
        allowed_org_ids = [
            oid for oid, entry in session.orgs.items()
            if entry.role == UserRole.ADMIN or ORG_USERS in entry.permissions
        ]
        if not allowed_org_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        org_ids = [uuid.UUID(oid) for oid in allowed_org_ids]

    return await service.get_accessible_users(org_ids=org_ids)


@router.get("/{user_id}", response_model=AdminUserDetailSchema, summary="Obtener detalle de usuario")
async def get_user(user_id: uuid.UUID, session: CurrentSession, service: UserServiceDep):
    return await service.get_user_detail(user_id)


@router.patch("/{user_id}", response_model=AdminUserDetailSchema, summary="Actualizar datos de usuario")
async def update_user(user_id: uuid.UUID, data: UpdateUserSchema, session: CurrentSession, service: UserServiceDep):
    return await service.update_user(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar usuario")
async def delete_user(user_id: uuid.UUID, payload: TokenPayload, service: UserServiceDep):
    calling_user_id = uuid.UUID(str(payload["sub"]))
    if calling_user_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes eliminarte a ti mismo.")
    await service.soft_delete_user(user_id)
