from __future__ import annotations

import uuid

from fastapi import HTTPException, status

from database.redis import RedisClient
from organizations.repository.organization_membership_repository import OrganizationMembershipRepository
from organizations.repository.organization_repository import OrganizationRepository
from organizations.services.organization_service import OrganizationService
from security.role_permissions_catalog import get_base_permissions
from users.enums.user_enums import PermissionEffect, UserRole, UserScope
from users.models.user_model import UserModel
from users.repository.permission_assignment_repository import PermissionAssignmentRepository
from users.repository.role_assignment_repository import RoleAssignmentRepository
from users.repository.user_repository import UserRepository
from users.schemas.user_session_schema import OrgSessionEntry, UserSession, session_key


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        org_repo: OrganizationRepository,
        membership_repo: OrganizationMembershipRepository,
        role_assignment_repo: RoleAssignmentRepository,
        permission_assignment_repo: PermissionAssignmentRepository,
        redis: RedisClient | None = None,
    ):
        self.user_repo = user_repo
        self.org_repo = org_repo
        self.membership_repo = membership_repo
        self.role_assignment_repo = role_assignment_repo
        self.permission_assignment_repo = permission_assignment_repo
        self._org_service = OrganizationService(org_repo, membership_repo, role_assignment_repo)
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
        doc_number = user.document_number

        if not assignments:
            session = UserSession(
                user_id=user_id,
                full_name=user.full_name,
                email=user.email,
                role=UserRole.USER,
                scope=UserScope.SELF,
                document_type=doc_type,
                document_number=doc_number,
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
                        )
                session = UserSession(
                    user_id=user_id,
                    full_name=user.full_name,
                    email=user.email,
                    document_type=doc_type,
                    document_number=doc_number,
                    scope=UserScope.ORGANIZATION,
                    orgs=orgs,
                )

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

        # Cascade: delete orgs where this user is admin (takes their memberships with them)
        for org_id in admin_org_ids:
            await self._org_service.soft_delete_organization(org_id)

        # Soft delete user's remaining memberships in orgs they didn't own
        remaining_memberships = await self.membership_repo.get_by_user_id(user_id)
        for membership in remaining_memberships:
            if membership.organization_id not in admin_org_ids:
                await self.membership_repo.delete(membership)

        user = await self.user_repo.get_by_id(user_id)
        if user is not None:
            await self.user_repo.delete(user)

    async def get_accessible_users(self, session: UserSession) -> list[UserModel]:
        if session.scope == UserScope.GLOBAL:
            return list(await self.user_repo.get_accessible(org_ids=None))
        if session.scope == UserScope.ORGANIZATION:
            org_ids = [uuid.UUID(o) for o in session.orgs.keys()]
            return list(await self.user_repo.get_accessible(org_ids=org_ids))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")

    async def restore_user(self, user_id: int) -> UserModel | None:
        user = await self.user_repo.get_by_id_including_deleted(user_id)
        if user is None or user.deleted_at is None:
            return user

        await self.user_repo.restore(user)

        admin_org_ids = await self.role_assignment_repo.get_admin_org_ids(user_id)

        # Cascade: restore orgs where this user is admin (and their memberships)
        for org_id in admin_org_ids:
            await self._org_service.restore_organization(org_id)

        # Restore user's memberships in orgs they didn't own
        all_memberships = await self.membership_repo.get_by_user_id_including_deleted(user_id)
        for membership in all_memberships:
            if membership.organization_id not in admin_org_ids and membership.deleted_at is not None:
                await self.membership_repo.restore(membership)

        return user
