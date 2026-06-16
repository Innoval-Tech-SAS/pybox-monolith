import uuid
from pathlib import Path
from typing import Sequence

from core.config.logger import logger

from fastapi import HTTPException, status

from core.tools.file_tools import save_org_document_bytes
from app_platform.countries.enums.country_enums import (
    Nationality,
    UserDocumentType,
    ORG_FISCAL_DOCUMENT_BY_NATIONALITY,
    ORG_MERCANTILE_DOCUMENT_BY_NATIONALITY,
)
from identity.organizations.models.organization_membership_model import OrganizationMembershipModel
from identity.organizations.models.organization_model import OrganizationModel
from identity.organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from identity.organizations.repository.organization_repository import OrganizationRepository
from identity.organizations.schemas.organization_schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    RepresentativeMode,
)
from core.security.services.encrypt_service import encrypt_service
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.models.role_assignment_model import RoleAssignmentModel
from identity.users.models.user_model import UserModel
from identity.users.repository.role_assignment_repository import RoleAssignmentRepository
from identity.users.repository.user_repository import UserRepository


class OrganizationService:
    def __init__(
        self,
        org_repo: OrganizationRepository,
        membership_repo: OrganizationMembershipRepository,
        role_assignment_repo: RoleAssignmentRepository,
        user_repo: UserRepository | None = None,
    ):
        self.org_repo = org_repo
        self.membership_repo = membership_repo
        self.role_assignment_repo = role_assignment_repo
        self.user_repo = user_repo

    # ── Queries ──────────────────────────────────────────────────────────────

    async def get_all(self) -> Sequence[OrganizationModel]:
        return await self.org_repo.get_all()

    async def get_for_user(self, user_id: int, scope: UserScope) -> Sequence[OrganizationModel]:
        if scope == UserScope.GLOBAL:
            return await self.org_repo.get_all()
        if scope == UserScope.ORGANIZATION:
            memberships = await self.membership_repo.get_by_user_id(user_id)
            org_ids = [m.organization_id for m in memberships]
            return await self.org_repo.get_by_ids(org_ids)
        return []

    async def get_by_id(self, org_id: uuid.UUID) -> OrganizationModel:
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organización no encontrada")
        return org

    # ── Ownership helper ─────────────────────────────────────────────────────

    async def _assert_admin_of_org(self, user_id: int, org_id: uuid.UUID) -> None:
        admin_org_ids = await self.role_assignment_repo.get_admin_org_ids(user_id)
        if org_id not in admin_org_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para gestionar esta organización",
            )

    # ── Write operations ─────────────────────────────────────────────────────

    async def create_organization(
        self,
        data: OrganizationCreate,
        created_by_user_id: int,
        scope: UserScope,
    ) -> OrganizationModel:
        org = OrganizationModel(**data.model_dump())
        org = await self.org_repo.add(org)

        if scope == UserScope.ORGANIZATION:
            membership = OrganizationMembershipModel(
                user_id=created_by_user_id,
                organization_id=org.id,
                created_by=created_by_user_id,
            )
            await self.membership_repo.add(membership)

            pending = await self.role_assignment_repo.get_pending_org_admin(created_by_user_id)
            if pending:
                pending.organization_id = org.id
                await self.role_assignment_repo.update(pending)
            else:
                assignment = RoleAssignmentModel(
                    user_id=created_by_user_id,
                    role=UserRole.ADMIN,
                    scope=UserScope.ORGANIZATION,
                    organization_id=org.id,
                )
                await self.role_assignment_repo.add(assignment)

        logger.info("[org] create | org_id=%s user_id=%d scope=%s", org.id, created_by_user_id, scope.value)
        return org

    async def register_with_representative(
        self,
        name: str,
        description: str | None,
        country: Nationality,
        fiscal_document_number: str | None,
        representative_mode: RepresentativeMode,
        representative_user_id: int | None,
        rep_firstname: str | None,
        rep_lastname: str | None,
        rep_email: str | None,
        rep_document_type: UserDocumentType | None,
        rep_document_number: str | None,
        fiscal_file_bytes: bytes,
        fiscal_file_ext: str,
        mercantile_file_bytes: bytes,
        mercantile_file_ext: str,
        representative_file_bytes: bytes,
        representative_file_ext: str,
        created_by_user_id: int,
        scope: UserScope,
    ) -> OrganizationModel:
        if self.user_repo is None:
            raise RuntimeError("user_repo is required for register_with_representative")

        # 1. Resolve legal representative user_id
        rep_user_id: int
        if representative_mode == RepresentativeMode.SELF:
            rep_user_id = created_by_user_id
        elif representative_mode == RepresentativeMode.SELECT:
            if not representative_user_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Debes seleccionar un representante legal.",
                )
            rep_user_id = representative_user_id
        else:  # CREATE
            for field, label in [
                (rep_firstname, "nombre"),
                (rep_lastname, "apellido"),
                (rep_email, "correo"),
                (rep_document_type, "tipo de documento"),
                (rep_document_number, "número de documento"),
            ]:
                if not field:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"El campo '{label}' es obligatorio para crear un representante.",
                    )
            existing = await self.user_repo.get_by_email(rep_email)  # type: ignore[arg-type]
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un usuario con ese correo electrónico.",
                )
            rep_doc_hash = encrypt_service.hash_document(rep_document_number) if rep_document_number else None
            new_user = UserModel(
                firstname=rep_firstname,
                lastname=rep_lastname,
                email=rep_email,
                document_type=rep_document_type,
                document_number=encrypt_service.encrypt_to_str(rep_document_number) if rep_document_number else None,
                document_number_hash=rep_doc_hash,
            )
            new_user = await self.user_repo.add(new_user)
            rep_user_id = new_user.id  # type: ignore[assignment]

        # 2. Pre-generate org id so filenames can reference it
        org_id = uuid.uuid4()
        org_id_str = str(org_id)

        # 3. Save files
        fiscal_file_path = save_org_document_bytes(fiscal_file_bytes, org_id_str, "fiscal", fiscal_file_ext)
        mercantile_file_path = save_org_document_bytes(mercantile_file_bytes, org_id_str, "mercantil", mercantile_file_ext)
        rep_file_path = save_org_document_bytes(representative_file_bytes, org_id_str, "representante", representative_file_ext)

        # 4. Resolve doc types from country
        fiscal_doc_type = ORG_FISCAL_DOCUMENT_BY_NATIONALITY.get(country)
        mercantile_doc_type = ORG_MERCANTILE_DOCUMENT_BY_NATIONALITY.get(country)

        # 5. Create organization
        org = OrganizationModel(
            id=org_id,
            name=name,
            description=description,
            country=country,
            fiscal_document_type=fiscal_doc_type,
            fiscal_document_number=encrypt_service.encrypt_to_str(fiscal_document_number) if fiscal_document_number else None,
            fiscal_document_file=fiscal_file_path,
            mercantile_document_type=mercantile_doc_type,
            mercantile_document_file=mercantile_file_path,
            representative_document_file=rep_file_path,
        )
        org = await self.org_repo.add(org)
        logger.info("[org] register_with_rep | org_id=%s mode=%s user_id=%d", org.id, representative_mode.value, created_by_user_id)

        # 6. Membership for legal representative (always with flag)
        rep_membership = OrganizationMembershipModel(
            user_id=rep_user_id,
            organization_id=org.id,
            created_by=created_by_user_id,
            is_legal_representative=True,
        )
        await self.membership_repo.add(rep_membership)

        # 7. Membership + role for the creating user (if different from rep)
        if created_by_user_id != rep_user_id:
            creator_membership = OrganizationMembershipModel(
                user_id=created_by_user_id,
                organization_id=org.id,
                created_by=created_by_user_id,
            )
            await self.membership_repo.add(creator_membership)

        # 8. Role assignment for creator
        if scope == UserScope.ORGANIZATION:
            pending = await self.role_assignment_repo.get_pending_org_admin(created_by_user_id)
            if pending:
                pending.organization_id = org.id
                await self.role_assignment_repo.update(pending)
            else:
                await self.role_assignment_repo.add(
                    RoleAssignmentModel(
                        user_id=created_by_user_id,
                        role=UserRole.ADMIN,
                        scope=UserScope.ORGANIZATION,
                        organization_id=org.id,
                    )
                )

        return org

    async def update_organization(
        self,
        org_id: uuid.UUID,
        data: OrganizationUpdate,
        requesting_user_id: int,
        scope: UserScope,
    ) -> OrganizationModel:
        if scope == UserScope.ORGANIZATION:
            await self._assert_admin_of_org(requesting_user_id, org_id)

        org = await self.get_by_id(org_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            if field == "fiscal_document_number" and value is not None:
                value = encrypt_service.encrypt_to_str(value)
            setattr(org, field, value)

        updated = await self.org_repo.update(org)
        logger.info("[org] update | org_id=%s user_id=%d", org_id, requesting_user_id)
        return updated

    async def delete_organization(
        self,
        org_id: uuid.UUID,
        requesting_user_id: int,
        scope: UserScope,
    ) -> None:
        if scope == UserScope.ORGANIZATION:
            await self._assert_admin_of_org(requesting_user_id, org_id)

        await self.get_by_id(org_id)  # raises 404 if not found

        memberships = await self.membership_repo.get_by_organization_id(org_id)
        for membership in memberships:
            await self.membership_repo.delete(membership)

        org = await self.org_repo.get_by_id(org_id)
        await self.org_repo.delete(org)

    # ── Soft-delete cascade (called from UserService) ─────────────────────────

    async def soft_delete_organization(self, org_id: uuid.UUID) -> None:
        memberships = await self.membership_repo.get_by_organization_id(org_id)
        for membership in memberships:
            await self.membership_repo.delete(membership)

        org = await self.org_repo.get_by_id(org_id)
        if org is not None:
            await self.org_repo.delete(org)

    async def restore_organization(self, org_id: uuid.UUID) -> OrganizationModel | None:
        org = await self.org_repo.get_by_id_including_deleted(org_id)
        if org is None or org.deleted_at is None:
            return org

        await self.org_repo.restore(org)

        memberships = await self.membership_repo.get_by_organization_id_including_deleted(org_id)
        for membership in memberships:
            if membership.deleted_at is not None:
                await self.membership_repo.restore(membership)

        return org
