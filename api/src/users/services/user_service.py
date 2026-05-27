from __future__ import annotations

import uuid

from fastapi import HTTPException, UploadFile, status

from database.redis import RedisClient
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from organizations.repository.organization_repository import OrganizationRepository
from organizations.services.organization_service import OrganizationService
from security.role_permissions_catalog import get_base_permissions
from security.services.encrypt_service import encrypt_service
from config.logger import logger
from tools.file_tools import delete_public_upload, save_profile_photo_file
from users.enums.user_enums import PermissionEffect, UserRole, UserScope
from users.models.role_assignment_model import RoleAssignmentModel
from users.models.user_model import UserModel
from users.repository.permission_assignment_repository import PermissionAssignmentRepository
from users.repository.role_assignment_repository import RoleAssignmentRepository
from users.repository.user_preferences_repository import UserPreferencesRepository
from users.repository.user_repository import UserRepository
from users.schemas.user_schemas import (
    AdminUserDetailSchema,
    AdminUserSummarySchema,
    ProfilePhotoSchema,
    RoleEntrySchema,
    UpdateUserSchema,
)
from users.schemas.user_session_schema import OrgSessionEntry, UserSession, session_key


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        membership_repo: OrganizationMembershipRepository,
        role_assignment_repo: RoleAssignmentRepository,
        permission_assignment_repo: PermissionAssignmentRepository,
        preferences_repo: UserPreferencesRepository,
        redis: RedisClient | None = None,
    ):
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.membership_repo = membership_repo
        self.role_assignment_repo = role_assignment_repo
        self.permission_assignment_repo = permission_assignment_repo
        self.preferences_repo = preferences_repo
        self._redis = redis

    @property
    def redis(self) -> RedisClient:
        if self._redis is None:
            from database.redis import redis_client
            self._redis = redis_client
        return self._redis

    async def get_user_session(self, user_id: int) -> UserSession:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

        assignments = await self.role_assignment_repo.get_by_user_id(user_id)

        doc_type = user.document_type.value if user.document_type else None
        doc_number = encrypt_service.decrypt_to_str(user.document_number) if user.document_number else None
        must_change_pw = user.must_change_password
        mfa_enabled = user.mfa_enabled

        if not assignments:
            session = UserSession(
                user_id=user_id,
                full_name=user.full_name,
                email=user.email,
                role=UserRole.USER,
                scope=UserScope.SELF,
                document_type=doc_type,
                document_number=doc_number,
                must_change_password=must_change_pw,
                mfa_enabled=mfa_enabled,
            )
        else:
            scopes = {a.scope for a in assignments}

            if UserScope.GLOBAL in scopes:
                global_assignment = next(a for a in assignments if a.scope == UserScope.GLOBAL)
                session = UserSession(
                    user_id=user_id,
                    full_name=user.full_name,
                    email=user.email,
                    role=global_assignment.role,
                    scope=UserScope.GLOBAL,
                    document_type=doc_type,
                    document_number=doc_number,
                    mfa_enabled=mfa_enabled,
                )
            elif UserScope.SELF in scopes and UserScope.ORGANIZATION not in scopes:
                self_assignment = next(a for a in assignments if a.scope == UserScope.SELF)
                session = UserSession(
                    user_id=user_id,
                    full_name=user.full_name,
                    email=user.email,
                    role=self_assignment.role,
                    scope=UserScope.SELF,
                    document_type=doc_type,
                    document_number=doc_number,
                    mfa_enabled=mfa_enabled,
                )
            else:
                memberships = await self.membership_repo.get_by_user_id(user_id)
                org_ids = [m.organization_id for m in memberships]
                org_models = {str(o.id): o for o in await self.org_repo.get_by_ids(org_ids)}
                assignment_by_org = {
                    str(a.organization_id): a
                    for a in assignments
                    if a.organization_id is not None
                }
                orgs = {}
                for m in memberships:
                    org_id_str = str(m.organization_id)
                    assignment = assignment_by_org.get(org_id_str)
                    org = org_models.get(org_id_str)
                    if assignment and org:
                        base = get_base_permissions(assignment.role)
                        overrides = await self.permission_assignment_repo.get_overrides_for_user_org(
                            user_id, m.organization_id
                        )
                        grants = {name for name, effect in overrides if effect == PermissionEffect.GRANT}
                        revokes = {name for name, effect in overrides if effect == PermissionEffect.REVOKE}
                        orgs[org_id_str] = OrgSessionEntry(
                            role=assignment.role,
                            org_name=org.name,
                            permissions=(base | grants) - revokes,
                            verification_status=org.verification_status,
                            created_at=org.created_at,
                        )
                session = UserSession(
                    user_id=user_id,
                    full_name=user.full_name,
                    email=user.email,
                    document_type=doc_type,
                    document_number=doc_number,
                    scope=UserScope.ORGANIZATION,
                    mfa_enabled=mfa_enabled,
                    orgs=orgs,
                )

        session.profile_photo_url = user.profile_photo_url
        await self.redis.set_json(session_key(user_id), session)
        return session

    async def get_profile(self, user_id: int) -> UserModel:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado.",
            )
        return user

    async def soft_delete_user(self, user_id: int) -> None:
        admin_org_ids = await self.role_assignment_repo.get_admin_org_ids(user_id)

        for org_id in admin_org_ids:
            await self._org_service.soft_delete_organization(org_id)

        remaining_memberships = await self.membership_repo.get_by_user_id(user_id)
        for membership in remaining_memberships:
            if membership.organization_id not in admin_org_ids:
                await self.membership_repo.delete(membership)

        user = await self.user_repo.get_by_id(user_id)
        if user is not None:
            await self.user_repo.delete(user)

    async def _build_role_entries(self, assignments: list[RoleAssignmentModel]) -> list[RoleEntrySchema]:
        org_ids = [a.organization_id for a in assignments if a.organization_id]
        orgs = {o.id: o for o in await self.org_repo.get_by_ids(org_ids)} if org_ids else {}
        return [
            RoleEntrySchema(
                role=a.role.value,
                scope=a.scope.value,
                org_id=str(a.organization_id) if a.organization_id else None,
                org_name=orgs[a.organization_id].name if a.organization_id and a.organization_id in orgs else None,
            )
            for a in assignments
        ]

    async def _enrich_users(self, users: list[UserModel]) -> list[AdminUserSummarySchema]:
        if not users:
            return []
        user_ids = [u.id for u in users]
        assignments = await self.role_assignment_repo.get_by_user_ids(user_ids)
        org_ids = list({a.organization_id for a in assignments if a.organization_id})
        orgs = {o.id: o for o in await self.org_repo.get_by_ids(org_ids)} if org_ids else {}

        assignments_by_user: dict[int, list[RoleAssignmentModel]] = {}
        for a in assignments:
            assignments_by_user.setdefault(a.user_id, []).append(a)

        return [
            AdminUserSummarySchema(
                id=u.id,
                full_name=u.full_name,
                email=u.email,
                phone_number=u.phone_number,
                is_active=u.is_active,
                created_at=u.created_at,
                roles=[
                    RoleEntrySchema(
                        role=a.role.value,
                        scope=a.scope.value,
                        org_id=str(a.organization_id) if a.organization_id else None,
                        org_name=orgs[a.organization_id].name if a.organization_id and a.organization_id in orgs else None,
                    )
                    for a in assignments_by_user.get(u.id, [])
                ],
            )
            for u in users
        ]

    async def get_accessible_users(self, session: UserSession, org_id: str | None = None) -> list[AdminUserSummarySchema]:
        if session.scope == UserScope.GLOBAL:
            if org_id:
                users = list(await self.user_repo.get_accessible(org_ids=[uuid.UUID(org_id)]))
            else:
                users = list(await self.user_repo.get_accessible(org_ids=None))
        elif session.scope == UserScope.ORGANIZATION:
            accessible_org_ids = [uuid.UUID(o) for o in session.orgs.keys()]
            if org_id:
                target = uuid.UUID(org_id)
                if target not in accessible_org_ids:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
                users = list(await self.user_repo.get_accessible(org_ids=[target]))
            else:
                users = list(await self.user_repo.get_accessible(org_ids=accessible_org_ids))
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")
        return await self._enrich_users(users)

    async def get_user_detail(self, user_id: int) -> AdminUserDetailSchema:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
        assignments = await self.role_assignment_repo.get_by_user_id(user_id)
        roles = await self._build_role_entries(assignments)
        return AdminUserDetailSchema(
            id=user.id,
            full_name=user.full_name,
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            phone_number=user.phone_number,
            auth_provider=user.auth_provider.value,
            document_type=user.document_type.value if user.document_type else None,
            document_number=encrypt_service.decrypt_to_str(user.document_number) if user.document_number else None,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            mfa_enabled=user.mfa_enabled,
            is_active_sessions=user.is_active_sessions,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=roles,
        )

    async def update_user(self, user_id: int, data: UpdateUserSchema) -> AdminUserDetailSchema:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
        if data.firstname is not None:
            user.firstname = data.firstname
        if data.lastname is not None:
            user.lastname = data.lastname
        if data.email is not None:
            user.email = data.email
        if data.phone_number is not None:
            user.phone_number = data.phone_number
        if data.is_active is not None:
            user.is_active = data.is_active
        await self.user_repo.update(user)
        return await self.get_user_detail(user_id)

    async def update_profile_photo(self, user_id: int, file: UploadFile) -> ProfilePhotoSchema:
        logger.debug("[profile-photo] service update start user_id=%s filename=%s", user_id, file.filename)
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            logger.debug("[profile-photo] service update user missing user_id=%s", user_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

        previous_url = user.profile_photo_url
        logger.debug("[profile-photo] service previous url user_id=%s previous_url=%s", user_id, previous_url)
        profile_photo_url = await save_profile_photo_file(file, user_id)
        user.profile_photo_url = profile_photo_url
        await self.user_repo.update(user)
        delete_public_upload(previous_url)
        await self.get_user_session(user_id)
        logger.debug("[profile-photo] service update done user_id=%s profile_photo_url=%s", user_id, profile_photo_url)
        return ProfilePhotoSchema(profile_photo_url=profile_photo_url)

    async def get_dismissed_tours(self, user_id: int) -> list[str]:
        prefs = await self.preferences_repo.get_by_user_id(user_id)
        return prefs.dismissed_tours if prefs else []

    async def dismiss_tour(self, user_id: int, tour_key: str) -> list[str]:
        prefs = await self.preferences_repo.dismiss_tour(user_id, tour_key)
        return prefs.dismissed_tours

    async def restore_user(self, user_id: int) -> UserModel | None:
        user = await self.user_repo.get_by_id_including_deleted(user_id)
        if user is None or user.deleted_at is None:
            return user
        await self.user_repo.restore(user)
        admin_org_ids = await self.role_assignment_repo.get_admin_org_ids(user_id)
        for org_id in admin_org_ids:
            await self._org_service.restore_organization(org_id)
        all_memberships = await self.membership_repo.get_by_user_id_including_deleted(user_id)
        for membership in all_memberships:
            if membership.organization_id not in admin_org_ids and membership.deleted_at is not None:
                await self.membership_repo.restore(membership)
        return user

    @property
    def _org_service(self) -> OrganizationService:
        return OrganizationService(self.org_repo, self.membership_repo, self.role_assignment_repo)
