from typing import cast

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from countries.enums.country_enums import (
    ORG_FISCAL_DOCUMENT_BY_NATIONALITY,
    ORG_MERCANTILE_DOCUMENT_BY_NATIONALITY,
)
from notifications.dependencies import get_verification_service
from notifications.enums.notification_enums import VerificationChannel
from onboarding.schemas.onboarding_schemas import (
    OnboardingStatusSchema,
    OrganizationOnboardingSchema,
    UpdateProfileSchema,
)
from organizations.models.organization_model import OrganizationModel
from organizations.models.organization_membership_model import OrganizationMembershipModel
from organizations.repository.organization_repository import OrganizationRepository
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from tools.file_tools import save_upload_file
from users.models.user_model import UserModel
from users.enums.user_enums import UserScope
from users.repository.user_repository import UserRepository


class OnboardingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._org_repo = OrganizationRepository(session)
        self._membership_repo = OrganizationMembershipRepository(session)

    def get_status(
        self,
        user: UserModel,
        scope: UserScope,
        org: OrganizationModel | None = None,
    ) -> OnboardingStatusSchema:
        email_verified = bool(user.is_email_verified)
        phone_verified = bool(user.is_phone_verified)
        document_complete = bool(user.document_type and user.document_number)

        missing: list[str] = []
        if not email_verified:
            missing.append("email_verification")
        if not phone_verified:
            missing.append("phone_verification")
        if not document_complete:
            missing.append("profile_document")

        org_complete: bool | None = None
        if scope == UserScope.ORGANIZATION:
            org_complete = (
                org is not None
                and bool(org.country)
                and bool(org.fiscal_document_number)
                and bool(org.fiscal_document_file)
                and bool(org.mercantile_document_file)
            )
            if not org_complete:
                missing.append("organization_data")

        base_complete = email_verified and phone_verified and document_complete
        is_complete = base_complete if scope == UserScope.SELF else base_complete and bool(org_complete)

        return OnboardingStatusSchema(
            email_verified=email_verified,
            phone_verified=phone_verified,
            document_complete=document_complete,
            org_complete=org_complete,
            is_complete=is_complete,
            missing_steps=missing,
        )

    async def request_otp(self, user: UserModel, channel: VerificationChannel) -> None:
        service = get_verification_service(channel, self._session)
        await service.send_code(user)

    async def verify_otp(self, user: UserModel, channel: VerificationChannel, code: str) -> None:
        service = get_verification_service(channel, self._session)
        await service.verify_code(user.id, code)

        if channel == VerificationChannel.EMAIL:
            user.is_email_verified = True
        else:
            user.is_phone_verified = True

        await self._user_repo.update(user)

    async def update_profile(self, user: UserModel, data: UpdateProfileSchema) -> None:
        user.document_type = data.document_type
        user.document_number = data.document_number
        user.nationality = data.nationality
        await self._user_repo.update(user)

    async def save_organization(
        self,
        user: UserModel,
        data: OrganizationOnboardingSchema,
        fiscal_file: UploadFile,
        mercantile_file: UploadFile,
    ) -> OrganizationModel:
        org = await self._org_repo.add(OrganizationModel(name=data.name))
        await self._membership_repo.add(OrganizationMembershipModel(
            user_id=cast(int, user.id),
            organization_id=org.id,
            created_by=cast(int, user.id),
        ))

        org_id = str(org.id)
        fiscal_path = await save_upload_file(fiscal_file, org_id, "fiscal")
        mercantile_path = await save_upload_file(mercantile_file, org_id, "mercantile")

        org.country = data.country
        org.fiscal_document_type = ORG_FISCAL_DOCUMENT_BY_NATIONALITY[data.country]
        org.fiscal_document_number = data.fiscal_document_number
        org.fiscal_document_file = fiscal_path
        org.mercantile_document_type = ORG_MERCANTILE_DOCUMENT_BY_NATIONALITY[data.country]
        org.mercantile_document_file = mercantile_path
        return await self._org_repo.update(org)
