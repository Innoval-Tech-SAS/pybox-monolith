"""Tests de `ChatService` para chats grupales -- foco en la regla de elegibilidad
de `_resolve_pinned_organization` (tenant-isolation): un candidato GLOBAL siempre
entra; uno ORGANIZATION-scoped solo si comparte organización con el grupo (o con el
propio actor mientras el grupo sigue sin pinear); nunca se acepta un organization_id
que venga del cliente -- se deriva siempre de filas reales de membresía/rol."""

import uuid

import pytest
from fastapi import HTTPException

from app_platform.chats.enums.chat_enums import ChatType
from app_platform.chats.repository.chat_repository import ChatRepository
from app_platform.chats.repository.message_repository import MessageRepository
from app_platform.chats.services.chat_service import ChatService
from identity.organizations.models.organization_membership_model import OrganizationMembershipModel
from identity.organizations.repository.organization_membership_repository import (
    OrganizationMembershipRepository,
)
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.models.role_assignment_model import RoleAssignmentModel
from identity.users.models.user_model import UserModel
from identity.users.repository.role_assignment_repository import RoleAssignmentRepository
from identity.users.repository.user_repository import UserRepository
from tests.receivables.conftest import build_organization


def build_user(**overrides) -> UserModel:
    suffix = uuid.uuid4().hex[:8]
    defaults = dict(firstname="Test", lastname=f"User {suffix}", email=f"{suffix}@example.com")
    defaults.update(overrides)
    return UserModel(**defaults)


@pytest.fixture
def chat_service(db_session) -> ChatService:
    return ChatService(
        chat_repo=ChatRepository(db_session),
        msg_repo=MessageRepository(db_session),
        user_repo=UserRepository(db_session),
        org_membership_repo=OrganizationMembershipRepository(db_session),
        role_assignment_repo=RoleAssignmentRepository(db_session),
    )


@pytest.fixture
async def two_orgs(db_session):
    org_x = build_organization()
    org_y = build_organization()
    db_session.add_all([org_x, org_y])
    await db_session.flush()
    return org_x, org_y


async def add_org_member(db_session, user: UserModel, org_id: uuid.UUID) -> None:
    db_session.add(
        OrganizationMembershipModel(user_id=user.id, organization_id=org_id, created_by=user.id)
    )
    await db_session.flush()


async def make_global_user(db_session, **overrides) -> UserModel:
    user = build_user(**overrides)
    db_session.add(user)
    await db_session.flush()
    db_session.add(RoleAssignmentModel(user_id=user.id, role=UserRole.ADMIN, scope=UserScope.GLOBAL))
    await db_session.flush()
    return user


async def make_org_user(db_session, org_id: uuid.UUID, **overrides) -> UserModel:
    user = build_user(**overrides)
    db_session.add(user)
    await db_session.flush()
    await add_org_member(db_session, user, org_id)
    return user


def org_session(make_user_session_factory, user_id, org_id):
    from identity.users.schemas.user_session_schema import OrgSessionEntry

    return make_user_session_factory(
        user_id=user_id,
        role=UserRole.USER,
        scope=UserScope.ORGANIZATION,
        orgs={str(org_id): OrgSessionEntry(role=UserRole.USER, org_name="Org")},
    )


def global_session(make_user_session_factory, user_id):
    return make_user_session_factory(user_id=user_id, role=UserRole.ADMIN, scope=UserScope.GLOBAL, orgs={})


class TestCreateGroupChat:
    async def test_two_members_same_org_pins_group_to_that_org(
        self, db_session, chat_service, two_orgs, make_user_session_factory
    ):
        org_x, _org_y = two_orgs
        actor = await make_org_user(db_session, org_x.id)
        peer = await make_org_user(db_session, org_x.id)
        session = org_session(make_user_session_factory, actor.id, org_x.id)

        summary = await chat_service.create_group_chat(session, "Equipo X", [peer.id])

        chat = await chat_service.chat_repo.get_by_id(summary.id)
        assert chat.type == ChatType.GROUP
        assert chat.organization_id == org_x.id

    async def test_members_from_different_orgs_rejected(
        self, db_session, chat_service, two_orgs, make_user_session_factory
    ):
        org_x, org_y = two_orgs
        actor = await make_org_user(db_session, org_x.id)
        outsider = await make_org_user(db_session, org_y.id)
        session = org_session(make_user_session_factory, actor.id, org_x.id)

        with pytest.raises(HTTPException) as exc:
            await chat_service.create_group_chat(session, "Grupo mixto", [outsider.id])
        assert exc.value.status_code == 400

    async def test_global_candidate_is_always_eligible(
        self, db_session, chat_service, two_orgs, make_user_session_factory
    ):
        org_x, _org_y = two_orgs
        actor = await make_org_user(db_session, org_x.id)
        global_user = await make_global_user(db_session)
        session = org_session(make_user_session_factory, actor.id, org_x.id)

        summary = await chat_service.create_group_chat(session, "Con soporte", [global_user.id])

        chat = await chat_service.chat_repo.get_by_id(summary.id)
        assert chat.organization_id == org_x.id

    async def test_all_global_members_stay_global_only(
        self, db_session, chat_service, make_user_session_factory
    ):
        actor = await make_global_user(db_session)
        peer = await make_global_user(db_session)
        session = global_session(make_user_session_factory, actor.id)

        summary = await chat_service.create_group_chat(session, "Staff global", [peer.id])

        chat = await chat_service.chat_repo.get_by_id(summary.id)
        assert chat.organization_id is None

    async def test_candidate_without_org_or_global_scope_rejected(
        self, db_session, chat_service, two_orgs, make_user_session_factory
    ):
        """Un candidato sin membresía de organización ni rol GLOBAL (p. ej. un
        deudor SELF) nunca resuelve un scope válido -- cae en el mismo 400 genérico,
        sin filtrar que se trata específicamente de un deudor."""
        org_x, _org_y = two_orgs
        actor = await make_org_user(db_session, org_x.id)
        outsider = build_user()
        db_session.add(outsider)
        await db_session.flush()
        session = org_session(make_user_session_factory, actor.id, org_x.id)

        with pytest.raises(HTTPException) as exc:
            await chat_service.create_group_chat(session, "Grupo", [outsider.id])
        assert exc.value.status_code == 400


class TestAddMember:
    async def test_non_admin_member_cannot_add(
        self, db_session, chat_service, two_orgs, make_user_session_factory
    ):
        org_x, _org_y = two_orgs
        owner = await make_org_user(db_session, org_x.id)
        member = await make_org_user(db_session, org_x.id)
        candidate = await make_org_user(db_session, org_x.id)
        owner_session = org_session(make_user_session_factory, owner.id, org_x.id)
        summary = await chat_service.create_group_chat(owner_session, "Grupo", [member.id])

        member_session = org_session(make_user_session_factory, member.id, org_x.id)
        with pytest.raises(HTTPException) as exc:
            await chat_service.add_member(member_session, summary.id, candidate.id)
        assert exc.value.status_code == 403

    async def test_admin_cannot_add_member_from_other_org(
        self, db_session, chat_service, two_orgs, make_user_session_factory
    ):
        org_x, org_y = two_orgs
        owner = await make_org_user(db_session, org_x.id)
        peer = await make_org_user(db_session, org_x.id)
        outsider = await make_org_user(db_session, org_y.id)
        owner_session = org_session(make_user_session_factory, owner.id, org_x.id)
        summary = await chat_service.create_group_chat(owner_session, "Grupo", [peer.id])

        with pytest.raises(HTTPException) as exc:
            await chat_service.add_member(owner_session, summary.id, outsider.id)
        assert exc.value.status_code == 400

        # La organización del grupo no debe quedar mutada por el intento fallido.
        chat = await chat_service.chat_repo.get_by_id(summary.id)
        assert chat.organization_id == org_x.id

    async def test_global_actor_pins_global_only_group_to_new_member_org(
        self, db_session, chat_service, two_orgs, make_user_session_factory
    ):
        org_x, _org_y = two_orgs
        owner = await make_global_user(db_session)
        peer = await make_global_user(db_session)
        candidate = await make_org_user(db_session, org_x.id)
        owner_session = global_session(make_user_session_factory, owner.id)
        summary = await chat_service.create_group_chat(owner_session, "Grupo global", [peer.id])
        assert (await chat_service.chat_repo.get_by_id(summary.id)).organization_id is None

        updated_summary, _recipients = await chat_service.add_member(owner_session, summary.id, candidate.id)

        chat = await chat_service.chat_repo.get_by_id(updated_summary.id)
        assert chat.organization_id == org_x.id


class TestRemoveMember:
    async def test_member_can_remove_self(
        self, db_session, chat_service, two_orgs, make_user_session_factory
    ):
        org_x, _org_y = two_orgs
        owner = await make_org_user(db_session, org_x.id)
        member = await make_org_user(db_session, org_x.id)
        owner_session = org_session(make_user_session_factory, owner.id, org_x.id)
        summary = await chat_service.create_group_chat(owner_session, "Grupo", [member.id])

        member_session = org_session(make_user_session_factory, member.id, org_x.id)
        recipients = await chat_service.remove_member(member_session, summary.id, member.id)
        assert owner.id in recipients

        member_row = await chat_service.chat_repo.get_member(summary.id, member.id)
        assert member_row.left_at is not None

    async def test_non_admin_cannot_remove_another_member(
        self, db_session, chat_service, two_orgs, make_user_session_factory
    ):
        org_x, _org_y = two_orgs
        owner = await make_org_user(db_session, org_x.id)
        member_a = await make_org_user(db_session, org_x.id)
        member_b = await make_org_user(db_session, org_x.id)
        owner_session = org_session(make_user_session_factory, owner.id, org_x.id)
        summary = await chat_service.create_group_chat(owner_session, "Grupo", [member_a.id, member_b.id])

        member_a_session = org_session(make_user_session_factory, member_a.id, org_x.id)
        with pytest.raises(HTTPException) as exc:
            await chat_service.remove_member(member_a_session, summary.id, member_b.id)
        assert exc.value.status_code == 403
