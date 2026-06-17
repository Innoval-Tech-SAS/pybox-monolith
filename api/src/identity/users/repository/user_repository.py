from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from identity.auth.enums.auth_enums import AuthProvider
from core.base.soft_delete_repository_base import SoftDeleteRepositoryBase
from app_platform.countries.enums.country_enums import UserDocumentType
from ..models.user_model import UserModel


class UserRepository(SoftDeleteRepositoryBase[UserModel]):
    model_class = UserModel

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_email(self, email: str) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.email == email,
                UserModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def get_by_provider_identity(
        self,
        auth_provider: AuthProvider,
        provider_user_id: str,
    ) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.auth_provider == auth_provider)
            .where(UserModel.provider_user_id == provider_user_id)
            .where(UserModel.deleted_at.is_(None))
        )
        return result.scalars().first()

    async def get_by_phone_number(self, phone_number: str) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel).where(
                UserModel.phone_number == phone_number,
                UserModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    async def get_by_document(
        self,
        document_type: UserDocumentType,
        document_number_hash: str,
    ) -> UserModel | None:
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.document_type == document_type)
            .where(UserModel.document_number_hash == document_number_hash)
            .where(UserModel.deleted_at.is_(None))
        )
        return result.scalars().first()

    async def get_all_active_except(self, self_id: uuid.UUID) -> Sequence[UserModel]:
        result = await self.session.execute(
            select(UserModel)
            .where(
                UserModel.id != self_id,
                UserModel.is_active.is_(True),
                UserModel.deleted_at.is_(None),
            )
            .order_by(UserModel.firstname)
        )
        return result.scalars().all()

    async def get_active_org_members(
        self, self_id: uuid.UUID, org_ids: list[uuid.UUID]
    ) -> Sequence[UserModel]:
        from identity.organizations.models.organization_membership_model import OrganizationMembershipModel
        result = await self.session.execute(
            select(UserModel)
            .join(OrganizationMembershipModel, OrganizationMembershipModel.user_id == UserModel.id)
            .where(
                OrganizationMembershipModel.organization_id.in_(org_ids),
                OrganizationMembershipModel.deleted_at.is_(None),
                UserModel.id != self_id,
                UserModel.is_active.is_(True),
                UserModel.deleted_at.is_(None),
            )
            .distinct()
            .order_by(UserModel.firstname)
        )
        return result.scalars().all()

    async def get_cs_org_members_and_global_cs(
        self, self_id: uuid.UUID, org_ids: list[uuid.UUID]
    ) -> Sequence[UserModel]:
        from sqlalchemy import or_
        from identity.organizations.models.organization_membership_model import OrganizationMembershipModel
        from identity.users.models.role_assignment_model import RoleAssignmentModel
        from identity.users.enums.user_enums import UserRole, UserScope

        org_members_subq = (
            select(OrganizationMembershipModel.user_id)
            .where(
                OrganizationMembershipModel.organization_id.in_(org_ids),
                OrganizationMembershipModel.deleted_at.is_(None),
            )
        )
        global_cs_subq = (
            select(RoleAssignmentModel.user_id)
            .where(
                RoleAssignmentModel.role == UserRole.CUSTOMER_SERVICE,
                RoleAssignmentModel.scope == UserScope.GLOBAL,
            )
        )
        result = await self.session.execute(
            select(UserModel)
            .where(
                or_(
                    UserModel.id.in_(org_members_subq),
                    UserModel.id.in_(global_cs_subq),
                ),
                UserModel.id != self_id,
                UserModel.is_active.is_(True),
                UserModel.deleted_at.is_(None),
            )
            .order_by(UserModel.firstname)
        )
        return result.scalars().all()

    async def get_cs_agents_for_self_user(self, self_id: uuid.UUID) -> Sequence[UserModel]:
        from identity.organizations.models.organization_membership_model import OrganizationMembershipModel
        from identity.users.models.role_assignment_model import RoleAssignmentModel
        from identity.users.enums.user_enums import UserRole, UserScope
        from receivables.portfolios.models.portfolio_model import PortfolioModel
        from receivables.credits.models.credit_model import CreditModel
        from receivables.debtors.models.debtor_model import DebtorModel

        doc_hash_subq = (
            select(UserModel.document_number_hash)
            .where(UserModel.id == self_id)
            .scalar_subquery()
        )
        org_ids_subq = (
            select(PortfolioModel.organization_id)
            .join(CreditModel, CreditModel.portfolio_id == PortfolioModel.id)
            .join(DebtorModel, DebtorModel.id == CreditModel.debtor_id)
            .where(DebtorModel.document_number_hash == doc_hash_subq)
            .distinct()
        )
        cs_user_ids_subq = (
            select(RoleAssignmentModel.user_id)
            .where(
                RoleAssignmentModel.role == UserRole.CUSTOMER_SERVICE,
                RoleAssignmentModel.scope == UserScope.ORGANIZATION,
                RoleAssignmentModel.organization_id.in_(org_ids_subq),
            )
        )
        result = await self.session.execute(
            select(UserModel)
            .where(
                UserModel.id.in_(cs_user_ids_subq),
                UserModel.id != self_id,
                UserModel.is_active.is_(True),
                UserModel.deleted_at.is_(None),
            )
            .order_by(UserModel.firstname)
        )
        return result.scalars().all()

    async def get_global_admins_chatted_recently(
        self, self_id: uuid.UUID, hours: int = 48
    ) -> Sequence[UserModel]:
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import and_
        from app_platform.chats.models.chat_member_model import ChatMemberModel
        from app_platform.chats.models.message_model import MessageModel
        from identity.users.models.role_assignment_model import RoleAssignmentModel
        from identity.users.enums.user_enums import UserRole, UserScope

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        my_chat_ids_subq = (
            select(ChatMemberModel.chat_id)
            .where(ChatMemberModel.user_id == self_id, ChatMemberModel.left_at.is_(None))
        )
        admin_ids_subq = (
            select(RoleAssignmentModel.user_id)
            .where(
                RoleAssignmentModel.role == UserRole.ADMIN,
                RoleAssignmentModel.scope == UserScope.GLOBAL,
            )
        )
        recent_senders_subq = (
            select(MessageModel.sender_id)
            .where(
                MessageModel.chat_id.in_(my_chat_ids_subq),
                MessageModel.sender_id.in_(admin_ids_subq),
                MessageModel.created_at >= cutoff,
            )
            .distinct()
        )
        result = await self.session.execute(
            select(UserModel)
            .where(
                UserModel.id.in_(recent_senders_subq),
                UserModel.id != self_id,
                UserModel.is_active.is_(True),
                UserModel.deleted_at.is_(None),
            )
        )
        return result.scalars().all()

    async def get_accessible(self, org_ids: list[uuid.UUID] | None) -> Sequence[UserModel]:
        if org_ids is None:
            result = await self.session.execute(
                select(UserModel).where(UserModel.deleted_at.is_(None))
            )
        else:
            from identity.organizations.models.organization_membership_model import OrganizationMembershipModel
            result = await self.session.execute(
                select(UserModel)
                .join(OrganizationMembershipModel, OrganizationMembershipModel.user_id == UserModel.id)
                .where(
                    OrganizationMembershipModel.organization_id.in_(org_ids),
                    OrganizationMembershipModel.deleted_at.is_(None),
                    UserModel.deleted_at.is_(None),
                )
                .distinct()
            )
        return result.scalars().all()

