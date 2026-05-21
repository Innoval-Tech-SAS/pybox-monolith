from fastapi import status
from config.api_router import APIRouter

from auth.dependencies import AuthServiceDep, TokenPayload
from auth.schemas.auth_schemas import (
    AuthResponse,
    ProviderAuth,
    ProviderLogin,
    RefreshRequest,
    UserCreate,
    UserLogin,
)
from users.enums.user_enums import UserRole, UserScope

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(body: UserCreate, service: AuthServiceDep) -> AuthResponse:
    return await service.register_and_authenticate(body, UserRole.ADMIN, UserScope.ORGANIZATION)


@router.post("/register/user", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(body: UserCreate, service: AuthServiceDep) -> AuthResponse:
    return await service.register_and_authenticate(body, UserRole.USER, UserScope.SELF)


@router.post("/login", response_model=AuthResponse)
async def login(body: UserLogin, service: AuthServiceDep) -> AuthResponse:
    return await service.authenticate_user(body)


@router.post("/oauth", response_model=AuthResponse)
async def oauth_login(body: ProviderLogin, service: AuthServiceDep) -> AuthResponse:
    return await service.authenticate_provider_user(body)


@router.post("/oauth/login", response_model=AuthResponse)
async def oauth_existing_login(body: ProviderAuth, service: AuthServiceDep) -> AuthResponse:
    return await service.authenticate_existing_provider_user(body)


@router.post("/refresh", response_model=AuthResponse)
async def refresh(body: RefreshRequest, service: AuthServiceDep) -> AuthResponse:
    return await service.refresh_tokens(body.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(payload: TokenPayload, service: AuthServiceDep) -> dict:
    await service.logout(int(payload["sub"]))
    return {"message": "Sesión cerrada."}
