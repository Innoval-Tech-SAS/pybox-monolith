from fastapi import HTTPException, status
from config.api_router import APIRouter

from auth.dependencies import AuthServiceDep, TokenPayload
from auth.schemas.auth_schemas import (
    AuthResponse,
    ChangePasswordSchema,
    ForgotPasswordLookupResponse,
    ForgotPasswordLookupSchema,
    ForgotPasswordSendCodeSchema,
    ProviderAuth,
    ProviderLogin,
    RefreshRequest,
    ResetPasswordSchema,
    UserCreate,
    UserLogin,
)
from security.dependencies import CurrentSession
from users.enums.user_enums import UserRole, UserScope

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar administrador de organización",
)
async def register_admin(body: UserCreate, service: AuthServiceDep) -> AuthResponse:
    return await service.register_and_authenticate(body, UserRole.ADMIN, UserScope.ORGANIZATION)


@router.post(
    "/register/user",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario deudor",
)
async def register_user(body: UserCreate, service: AuthServiceDep) -> AuthResponse:
    return await service.register_and_authenticate(body, UserRole.USER, UserScope.SELF)


@router.post("/login", response_model=AuthResponse, summary="Iniciar sesión con correo y contraseña")
async def login(body: UserLogin, service: AuthServiceDep) -> AuthResponse:
    return await service.authenticate_user(body)


@router.post("/oauth", response_model=AuthResponse, summary="Registrar administrador con proveedor OAuth")
async def oauth_register_admin(body: ProviderLogin, service: AuthServiceDep) -> AuthResponse:
    return await service.authenticate_provider_user(body, UserRole.ADMIN, UserScope.ORGANIZATION)


@router.post("/oauth/user", response_model=AuthResponse, summary="Registrar usuario deudor con proveedor OAuth")
async def oauth_register_user(body: ProviderLogin, service: AuthServiceDep) -> AuthResponse:
    return await service.authenticate_provider_user(body, UserRole.USER, UserScope.SELF)


@router.post("/oauth/login", response_model=AuthResponse, summary="Iniciar sesión con proveedor OAuth existente")
async def oauth_existing_login(body: ProviderAuth, service: AuthServiceDep) -> AuthResponse:
    return await service.authenticate_existing_provider_user(body)


@router.post("/refresh", response_model=AuthResponse, summary="Renovar tokens de acceso")
async def refresh(body: RefreshRequest, service: AuthServiceDep) -> AuthResponse:
    return await service.refresh_tokens(body.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK, summary="Cerrar sesión")
async def logout(payload: TokenPayload, service: AuthServiceDep) -> dict:
    await service.logout(int(payload["sub"]))
    return {"message": "Sesión cerrada."}


@router.post("/logout/{user_id}", status_code=status.HTTP_200_OK, summary="Cerrar sesión de otro usuario (admin)")
async def force_logout(user_id: int, session: CurrentSession, service: AuthServiceDep) -> dict:
    is_org_admin = any(entry.role == UserRole.ADMIN for entry in session.orgs.values())
    if not session.is_global and not is_org_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Sin permisos para esta acción.")
    if session.user_id == user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Usa /auth/logout para cerrar tu propia sesión.")
    await service.logout(user_id)
    return {"message": "Sesión cerrada."}


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT, summary="Cambiar contraseña")
async def change_password(body: ChangePasswordSchema, session: CurrentSession, service: AuthServiceDep) -> None:
    try:
        await service.change_password(session.user_id, body.current_password, body.new_password)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.post("/forgot-password/lookup", response_model=ForgotPasswordLookupResponse, summary="Paso 1 — Buscar cuenta por documento")
async def forgot_password_lookup(body: ForgotPasswordLookupSchema, service: AuthServiceDep) -> ForgotPasswordLookupResponse:
    try:
        result = await service.lookup_user_for_reset(body.document_type.value, body.document_number)
        return ForgotPasswordLookupResponse(**result)
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post("/forgot-password/send-code", status_code=status.HTTP_204_NO_CONTENT, summary="Paso 2 — Enviar código al canal elegido")
async def forgot_password_send_code(body: ForgotPasswordSendCodeSchema, service: AuthServiceDep) -> None:
    try:
        await service.send_reset_code(body.document_type.value, body.document_number, body.channel)
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT, summary="Paso 3 — Confirmar código y nueva contraseña")
async def reset_password(body: ResetPasswordSchema, service: AuthServiceDep) -> None:
    try:
        await service.reset_password(body.document_type.value, body.document_number, body.code, body.channel, body.new_password)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
