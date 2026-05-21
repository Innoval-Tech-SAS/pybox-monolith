import json

from fastapi import APIRouter, Form, HTTPException, UploadFile, status

from notifications.exceptions import (
    CodeAlreadyUsedException,
    CodeExpiredException,
    CodeNotFoundException,
)
from onboarding.dependencies import (
    CurrentOrg,
    CurrentScope,
    CurrentUser,
    OnboardingServiceDep,
)
from onboarding.schemas.onboarding_schemas import (
    OnboardingStatusSchema,
    OrganizationOnboardingSchema,
    RequestOtpSchema,
    UpdateProfileSchema,
    VerifyOtpSchema,
)
from tools.file_tools import save_upload_file
from users.enums.user_enums import UserScope

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/status", response_model=OnboardingStatusSchema)
async def get_status(
    user: CurrentUser,
    scope: CurrentScope,
    org: CurrentOrg,
    service: OnboardingServiceDep,
):
    return service.get_status(user, scope, org)


@router.post("/request-otp", status_code=status.HTTP_204_NO_CONTENT)
async def request_otp(
    body: RequestOtpSchema,
    user: CurrentUser,
    service: OnboardingServiceDep,
):
    await service.request_otp(user, body.channel)


@router.post("/verify-otp", status_code=status.HTTP_204_NO_CONTENT)
async def verify_otp(
    body: VerifyOtpSchema,
    user: CurrentUser,
    service: OnboardingServiceDep,
):
    try:
        await service.verify_otp(user, body.channel, body.code)
    except CodeNotFoundException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código no encontrado")
    except CodeExpiredException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El código ha expirado")
    except CodeAlreadyUsedException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El código ya fue utilizado")


@router.patch("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def update_profile(
    body: UpdateProfileSchema,
    user: CurrentUser,
    service: OnboardingServiceDep,
):
    await service.update_profile(user, body)


@router.post("/organization", status_code=status.HTTP_204_NO_CONTENT)
async def update_organization(
    user: CurrentUser,
    scope: CurrentScope,
    org: CurrentOrg,
    service: OnboardingServiceDep,
    data: str = Form(...),
    fiscal_document_file: UploadFile = Form(...),
    mercantile_document_file: UploadFile = Form(...),
):
    if scope != UserScope.ORGANIZATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores de organización pueden completar este paso",
        )
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no pertenece a ninguna organización",
        )

    try:
        parsed = OrganizationOnboardingSchema.model_validate(json.loads(data))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El campo 'data' debe ser un JSON válido",
        )

    fiscal_path = await save_upload_file(fiscal_document_file, str(org.id), "fiscal")
    mercantile_path = await save_upload_file(mercantile_document_file, str(org.id), "mercantile")

    await service.save_organization(org, parsed, fiscal_path, mercantile_path)
