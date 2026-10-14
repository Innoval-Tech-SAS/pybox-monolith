"""Baja lógica de una organización: además de membresías, roles y portafolios arrastra
sus deudores y chats de WhatsApp (con lo que cuelga de ellos). Todo con el sello de la
organización: `restore_organization` revierte solo lo que cayó con ella.
"""

from identity.organizations.repository.organization_membership_repository import (
    OrganizationMembershipRepository,
)
from identity.organizations.repository.organization_repository import (
    OrganizationRepository,
)
from identity.organizations.services.organization_service import OrganizationService
from identity.users.repository.role_assignment_repository import (
    RoleAssignmentRepository,
)
from identity.users.repository.user_repository import UserRepository
from messaging.whatsapp.repository.whatsapp_chat_repository import (
    WhatsAppChatRepository,
)
from messaging.whatsapp.repository.whatsapp_message_repository import (
    WhatsAppMessageRepository,
)
from receivables.debtors.repository.debtor_repository import DebtorRepository
from tests.messaging.whatsapp.conftest import build_chat, build_message
from tests.receivables.conftest import add_organization, build_debtor


def build_service(db_session) -> OrganizationService:
    return OrganizationService(
        org_repo=OrganizationRepository(db_session),
        membership_repo=OrganizationMembershipRepository(db_session),
        role_assignment_repo=RoleAssignmentRepository(db_session),
        user_repo=UserRepository(db_session),
    )


async def _organization_with_debtor_and_chat(db_session):
    org = await add_organization(db_session)
    debtor = build_debtor(org.id)
    chat = build_chat(org.id)
    db_session.add_all([debtor, chat])
    await db_session.flush()
    message = build_message(chat.id)
    db_session.add(message)
    await db_session.flush()
    return org, debtor, chat, message


class TestSoftDeleteOrganizationData:
    async def test_cascades_to_debtors_and_whatsapp_chats_with_their_messages(
        self, db_session
    ):
        org, debtor, chat, message = await _organization_with_debtor_and_chat(
            db_session
        )

        await build_service(db_session).soft_delete_organization(org.id)
        db_session.expunge_all()  # el UPDATE en bloque no refresca lo ya cargado: forzar relectura

        assert await DebtorRepository(db_session).get_by_id(debtor.id) is None
        assert await WhatsAppChatRepository(db_session).get_by_id(chat.id) is None
        assert await WhatsAppMessageRepository(db_session).get_by_id(message.id) is None

    async def test_does_not_touch_other_organizations(self, db_session):
        org, *_ = await _organization_with_debtor_and_chat(db_session)
        _, other_debtor, other_chat, other_message = (
            await _organization_with_debtor_and_chat(db_session)
        )

        await build_service(db_session).soft_delete_organization(org.id)
        db_session.expunge_all()  # el UPDATE en bloque no refresca lo ya cargado: forzar relectura

        assert await DebtorRepository(db_session).get_by_id(other_debtor.id) is not None
        assert (
            await WhatsAppChatRepository(db_session).get_by_id(other_chat.id)
            is not None
        )
        assert (
            await WhatsAppMessageRepository(db_session).get_by_id(other_message.id)
            is not None
        )


class TestRestoreOrganizationData:
    async def test_restores_what_fell_with_the_organization(self, db_session):
        org, debtor, chat, message = await _organization_with_debtor_and_chat(
            db_session
        )
        service = build_service(db_session)
        await service.soft_delete_organization(org.id)
        db_session.expunge_all()  # el UPDATE en bloque no refresca lo ya cargado: forzar relectura

        await service.restore_organization(org.id)
        db_session.expunge_all()  # el UPDATE en bloque no refresca lo ya cargado: forzar relectura

        assert await DebtorRepository(db_session).get_by_id(debtor.id) is not None
        assert await WhatsAppChatRepository(db_session).get_by_id(chat.id) is not None
        assert (
            await WhatsAppMessageRepository(db_session).get_by_id(message.id)
            is not None
        )

    async def test_does_not_restore_a_debtor_deleted_before_the_organization(
        self, db_session
    ):
        org, _, _, _ = await _organization_with_debtor_and_chat(db_session)
        old_debtor = build_debtor(org.id)
        db_session.add(old_debtor)
        await db_session.flush()
        debtor_repo = DebtorRepository(db_session)
        await debtor_repo.delete(old_debtor)  # baja anterior, con su propio sello

        service = build_service(db_session)
        await service.soft_delete_organization(org.id)
        db_session.expunge_all()  # el UPDATE en bloque no refresca lo ya cargado: forzar relectura
        await service.restore_organization(org.id)
        db_session.expunge_all()  # el UPDATE en bloque no refresca lo ya cargado: forzar relectura

        assert await debtor_repo.get_by_id(old_debtor.id) is None
