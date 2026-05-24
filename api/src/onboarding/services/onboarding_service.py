
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from countries.enums.country_enums import (
    ORG_FISCAL_DOCUMENT_BY_NATIONALITY,
    ORG_MERCANTILE_DOCUMENT_BY_NATIONALITY,
)
from messaging.dependencies import get_verification_service
from messaging.enums.notification_enums import VerificationChannel
from onboarding.schemas.onboarding_schemas import (
    OnboardingStatusSchema,
    OrganizationOnboardingSchema,
    UpdateProfileSchema,
)
from auth.enums.auth_enums import AuthProvider
from onboarding.schemas.onboarding_schemas import OnboardingRepMode
from organizations.enums.organization_enums import VerificationStatus
from organizations.models.organization_model import OrganizationModel
from support.services.support_service import SupportService
from organizations.models.organization_membership_model import OrganizationMembershipModel
from organizations.repository.organization_repository import OrganizationRepository
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from tools.file_tools import save_upload_file
from users.enums.user_enums import UserScope
from users.models.user_model import UserModel
from users.repository.permission_assignment_repository import PermissionAssignmentRepository
from users.repository.role_assignment_repository import RoleAssignmentRepository
from users.repository.user_preferences_repository import UserPreferencesRepository
from users.repository.user_repository import UserRepository
from users.services.user_service import UserService


class OnboardingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._org_repo = OrganizationRepository(session)
        self._membership_repo = OrganizationMembershipRepository(session)
        self._role_repo = RoleAssignmentRepository(session)
        self._user_service = UserService(
            user_repo=self._user_repo,
            org_repo=self._org_repo,
            membership_repo=self._membership_repo,
            role_assignment_repo=self._role_repo,
            permission_assignment_repo=PermissionAssignmentRepository(session),
            preferences_repo=UserPreferencesRepository(session),
        )
        self._support_service = SupportService(session)

    async def get_status(
        self,
        user_id: int,
        scope: UserScope,
        org: OrganizationModel | None = None,
    ) -> OnboardingStatusSchema:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

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

    async def request_otp(self, user_id: int, channel: VerificationChannel) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
        service = get_verification_service(channel, self._session)
        await service.send_code(user)

    async def verify_otp(self, user_id: int, channel: VerificationChannel, code: str) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
        service = get_verification_service(channel, self._session)
        await service.verify_code(user_id, code)

        if channel == VerificationChannel.EMAIL:
            user.is_email_verified = True
        else:
            user.is_phone_verified = True

        await self._user_repo.update(user)

    async def update_profile(self, user_id: int, data: UpdateProfileSchema) -> None:
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
        user.document_type = data.document_type
        user.document_number = data.document_number
        user.nationality = data.nationality
        await self._user_repo.update(user)

    async def create_first_org(
        self,
        user_id: int,
        data: OrganizationOnboardingSchema,
        fiscal_file: UploadFile,
        mercantile_file: UploadFile,
        representative_file: UploadFile,
    ) -> OrganizationModel:
        org = await self._org_repo.add(OrganizationModel(name=data.name, verification_status=VerificationStatus.PENDING))

        org_id = str(org.id)
        fiscal_path = await save_upload_file(fiscal_file, org_id, "fiscal")
        mercantile_path = await save_upload_file(mercantile_file, org_id, "mercantile")
        representative_path = await save_upload_file(representative_file, org_id, "representative")

        org.country = data.country
        org.fiscal_document_type = ORG_FISCAL_DOCUMENT_BY_NATIONALITY[data.country]
        org.fiscal_document_number = data.fiscal_document_number
        org.fiscal_document_file = fiscal_path
        org.mercantile_document_type = ORG_MERCANTILE_DOCUMENT_BY_NATIONALITY[data.country]
        org.mercantile_document_file = mercantile_path
        org.representative_document_file = representative_path
        updated_org = await self._org_repo.update(org)

        if data.representative_mode == OnboardingRepMode.SELF:
            await self._membership_repo.add(OrganizationMembershipModel(
                user_id=user_id,
                organization_id=updated_org.id,
                created_by=user_id,
                is_legal_representative=True,
            ))
        else:
            await self._membership_repo.add(OrganizationMembershipModel(
                user_id=user_id,
                organization_id=updated_org.id,
                created_by=user_id,
            ))
            rep_user = await self._user_repo.add(UserModel(
                firstname=data.rep_firstname,
                lastname=data.rep_lastname,
                email=data.rep_email,
                hashed_password=None,
                auth_provider=AuthProvider.SELF,
                document_type=data.rep_document_type,
                document_number=data.rep_document_number,
            ))
            await self._membership_repo.add(OrganizationMembershipModel(
                user_id=rep_user.id,
                organization_id=updated_org.id,
                created_by=user_id,
                is_legal_representative=True,
            ))

        pending_role = await self._role_repo.get_pending_org_admin(user_id)
        if pending_role is not None:
            pending_role.organization_id = updated_org.id
            await self._role_repo.update(pending_role)

        await self._support_service.create_org_verification_ticket(updated_org.id, user_id)
        await self._user_service.get_user_session(user_id)

        return updated_org
