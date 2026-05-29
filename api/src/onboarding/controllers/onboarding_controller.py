import json

from fastapi import Form, HTTPException, UploadFile, status

from config.api_router import APIRouter
from messaging.exceptions import (
    CodeAlreadyUsedException,
    CodeExpiredException,
    CodeNotFoundException,
)
from onboarding.dependencies import (
    CurrentOrg,
    CurrentScope,
    OnboardingServiceDep,
)
from onboarding.schemas.onboarding_schemas import (
    OnboardingStatusSchema,
    OrganizationOnboardingSchema,
    RequestOtpSchema,
    SetOnboardingPasswordSchema,
    SetPhoneSchema,
    UpdateProfileSchema,
    VerifyOtpSchema,
)
from security.dependencies import CurrentSession
from users.enums.user_enums import UserScope

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get(
    "/status",
    response_model=OnboardingStatusSchema,
    summary="Consultar estado del onboarding",
    description="Indica qué pasos del onboarding ha completado el usuario y cuáles faltan.",
)
async def get_status(
    session: CurrentSession,
    scope: CurrentScope,
    org: CurrentOrg,
    service: OnboardingServiceDep,
):
    return await service.get_status(session.user_id, scope, org)


@router.post(
    "/request-otp",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Solicitar código OTP de verificación",
)
async def request_otp(
    body: RequestOtpSchema,
    session: CurrentSession,
    service: OnboardingServiceDep,
):
    await service.request_otp(session.user_id, body.channel)


@router.post(
    "/verify-otp",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Verificar código OTP",
)
async def verify_otp(
    body: VerifyOtpSchema,
    session: CurrentSession,
    service: OnboardingServiceDep,
):
    try:
        await service.verify_otp(session.user_id, body.channel, body.code)
    except CodeNotFoundException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código no encontrado")
    except CodeExpiredException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El código ha expirado")
    except CodeAlreadyUsedException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El código ya fue utilizado")


@router.patch(
    "/set-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Establecer contraseña inicial",
)
async def set_onboarding_password(
    body: SetOnboardingPasswordSchema,
    session: CurrentSession,
    service: OnboardingServiceDep,
):
    await service.set_onboarding_password(session.user_id, body)


@router.patch(
    "/phone",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Registrar número de teléfono",
)
async def set_phone(
    body: SetPhoneSchema,
    session: CurrentSession,
    service: OnboardingServiceDep,
):
    await service.set_phone(session.user_id, body)


@router.patch(
    "/profile",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Completar perfil con documento de identidad",
)
async def update_profile(
    body: UpdateProfileSchema,
    session: CurrentSession,
    service: OnboardingServiceDep,
):
    await service.update_profile(session.user_id, body)


@router.post(
    "/organization",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Crear primera organización",
    description="Paso de onboarding para administradores: registra la organización con sus documentos.",
)
async def create_first_org(
    session: CurrentSession,
    scope: CurrentScope,
    service: OnboardingServiceDep,
    data: str = Form(...),
    fiscal_document_file: UploadFile = Form(...),
    mercantile_document_file: UploadFile = Form(...),
    representative_document_file: UploadFile = Form(...),
):
    if scope != UserScope.ORGANIZATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores de organización pueden completar este paso",
        )

    try:
        parsed = OrganizationOnboardingSchema.model_validate(json.loads(data))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El campo 'data' debe ser un JSON válido",
        )

    await service.create_first_org(session.user_id, parsed, fiscal_document_file, mercantile_document_file, representative_document_file)
