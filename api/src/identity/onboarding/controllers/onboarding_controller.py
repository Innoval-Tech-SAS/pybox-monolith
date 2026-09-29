import json

from fastapi import Depends, Form, HTTPException, UploadFile, status

from core.config.api_router import APIRouter
from core.config.logger import logger
from core.security.dependencies import PendingMfaSession
from core.security.rate_limit import rate_limit
from identity.auth.exceptions import (
    CodeAlreadyUsedException,
    CodeExpiredException,
    CodeNotFoundException,
)
from identity.onboarding.dependencies import (
    OnboardingServiceDep,
    PendingMfaOrg,
    PendingMfaScope,
)
from identity.onboarding.schemas.onboarding_schemas import (
    IdentityDocumentSubmittedSchema,
    OnboardingStatusSchema,
    OrganizationOnboardingSchema,
    RequestOtpSchema,
    SetOnboardingPasswordSchema,
    SetPhoneSchema,
    UpdateProfileSchema,
    VerifyOtpSchema,
)
from identity.users.enums.user_enums import UserScope

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

# El código OTP es de 6 dígitos: sin límite de intentos es fuerza-bruteable.
_otp_rate_limit = Depends(
    rate_limit("onboarding-otp", max_attempts=10, window_seconds=300)
)


@router.get(
    "/status",
    response_model=OnboardingStatusSchema,
    summary="Consultar estado del onboarding",
    description=(
        "Indica qué pasos del onboarding ha completado el usuario y cuáles faltan."
    ),
)
async def get_status(
    session: PendingMfaSession,
    scope: PendingMfaScope,
    org: PendingMfaOrg,
    service: OnboardingServiceDep,
):
    return await service.get_status(session.user_id, scope, org)


@router.post(
    "/request-otp",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Solicitar código OTP de verificación",
    dependencies=[_otp_rate_limit],
)
async def request_otp(
    body: RequestOtpSchema,
    session: PendingMfaSession,
    service: OnboardingServiceDep,
):
    logger.info(
        "[onboarding] request_otp_start | user_id=%s channel=%s",
        session.user_id,
        body.channel.value,
    )
    await service.request_otp(session.user_id, body.channel)
    logger.info(
        "[onboarding] request_otp_done | user_id=%s channel=%s",
        session.user_id,
        body.channel.value,
    )


@router.post(
    "/verify-otp",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Verificar código OTP",
    dependencies=[_otp_rate_limit],
)
async def verify_otp(
    body: VerifyOtpSchema,
    session: PendingMfaSession,
    service: OnboardingServiceDep,
):
    logger.info(
        "[onboarding] verify_otp_start | user_id=%s channel=%s",
        session.user_id,
        body.channel.value,
    )
    try:
        await service.verify_otp(session.user_id, body.channel, body.code)
        logger.info(
            "[onboarding] verify_otp_done | user_id=%s channel=%s",
            session.user_id,
            body.channel.value,
        )
    except CodeNotFoundException as e:
        logger.warning(
            "[onboarding] verify_otp_failed | user_id=%s channel=%s reason=not_found",
            session.user_id,
            body.channel.value,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Código no encontrado"
        ) from e
    except CodeExpiredException as e:
        logger.warning(
            "[onboarding] verify_otp_failed | user_id=%s channel=%s reason=expired",
            session.user_id,
            body.channel.value,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El código ha expirado"
        ) from e
    except CodeAlreadyUsedException as e:
        logger.warning(
            "[onboarding] verify_otp_failed | user_id=%s channel=%s "
            "reason=already_used",
            session.user_id,
            body.channel.value,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El código ya fue utilizado"
        ) from e


@router.patch(
    "/set-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Establecer contraseña inicial",
)
async def set_onboarding_password(
    body: SetOnboardingPasswordSchema,
    session: PendingMfaSession,
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
    session: PendingMfaSession,
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
    session: PendingMfaSession,
    service: OnboardingServiceDep,
):
    await service.update_profile(session.user_id, body)


@router.patch(
    "/identity-document",
    response_model=IdentityDocumentSubmittedSchema,
    summary="Subir documento de identidad (titulares SELF)",
    description="Paso de onboarding para titulares: sube su documento de identidad "
    "(PDF o foto) y abre el ticket de validación. Gatea el acceso a "
    "/credits/my-credits, /statements/my-statements y "
    "/judicial-notifications/mine hasta que se apruebe.",
)
async def submit_identity_document(
    session: PendingMfaSession,
    scope: PendingMfaScope,
    service: OnboardingServiceDep,
    file: UploadFile,
):
    if scope != UserScope.SELF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo titulares pueden completar este paso",
        )
    identity_status = await service.submit_identity_document(session.user_id, file)
    return IdentityDocumentSubmittedSchema(identity_verification_status=identity_status)


@router.post(
    "/organization",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Crear primera organización",
    description="Paso de onboarding para administradores: registra la organización "
    "con sus documentos.",
)
async def create_first_org(
    session: PendingMfaSession,
    scope: PendingMfaScope,
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El campo 'data' debe ser un JSON válido",
        ) from e

    await service.create_first_org(
        session.user_id,
        parsed,
        fiscal_document_file,
        mercantile_document_file,
        representative_document_file,
    )
