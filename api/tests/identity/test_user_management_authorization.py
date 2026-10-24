"""Autorización sobre la cuenta de OTROS usuarios (editar, eliminar, permisos).

Riesgos cubiertos:
  * quien solo tiene `org.users` no puede tocar a un admin de la organización (tomar su
    cuenta cambiando el correo/MFA, o eliminarlo y arrastrar la organización);
  * nadie desde una organización toca a un usuario que también está en otra, ni a
    personal global (los cambios afectarían a otros tenants);
  * eliminar a quien administra una organización es solo de admin global;
  * eliminar/desactivar/cambiar permisos cierra la sesión cacheada y el refresh token;
  * los permisos por usuario solo se otorgan a miembros de la organización.
"""

import uuid

import pytest

from core.database.redis import redis_client
from core.security.constants.permissions import ORG_USERS
from core.security.services.auth_token_service import AuthTokenService
from identity.organizations.enums.organization_enums import VerificationStatus
from identity.organizations.models.organization_membership_model import (
    OrganizationMembershipModel,
)
from identity.organizations.repository.organization_repository import (
    OrganizationRepository,
)
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.models.role_assignment_model import RoleAssignmentModel
from identity.users.schemas.user_session_schema import OrgSessionEntry, session_key
from tests.factories import get_user_by_email, register_payload
from tests.receivables.conftest import add_organization

AUTH_BASE = "/api/v1/auth"
USERS_BASE = "/api/v1/users"
ORG_BASE = "/api/v1/organizations"


async def _new_user(client, db_session) -> uuid.UUID:
    payload = register_payload()
    resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
    assert resp.status_code == 201
    return (await get_user_by_email(db_session, payload["email"])).id


async def _add_member(db_session, user_id, org_id, role: UserRole) -> None:
    db_session.add_all(
        [
            OrganizationMembershipModel(
                user_id=user_id, organization_id=org_id, created_by=user_id
            ),
            RoleAssignmentModel(
                user_id=user_id,
                role=role,
                scope=UserScope.ORGANIZATION,
                organization_id=org_id,
            ),
        ]
    )
    await db_session.flush()


def _org_session(
    make_user_session_factory,
    user_id,
    orgs: dict[uuid.UUID, tuple[UserRole, frozenset[str]]],
):
    return make_user_session_factory(
        user_id=user_id,
        role=next(iter(orgs.values()))[0],
        scope=UserScope.ORGANIZATION,
        orgs={
            str(org_id): OrgSessionEntry(
                role=role,
                org_name="Org",
                permissions=permissions,
                verification_status=VerificationStatus.APPROVED,
            )
            for org_id, (role, permissions) in orgs.items()
        },
    )


@pytest.fixture
async def org(db_session):
    return await add_organization(db_session)


@pytest.fixture
async def org_admin_id(client, db_session, org):
    user_id = await _new_user(client, db_session)
    await _add_member(db_session, user_id, org.id, UserRole.ADMIN)
    return user_id


@pytest.fixture
async def member_id(client, db_session, org):
    user_id = await _new_user(client, db_session)
    await _add_member(db_session, user_id, org.id, UserRole.USER)
    return user_id


@pytest.fixture
async def users_manager_id(client, db_session, org):
    """Miembro sin rol de admin al que se le dio `org.users`."""
    user_id = await _new_user(client, db_session)
    await _add_member(db_session, user_id, org.id, UserRole.USER)
    return user_id


class TestUpdateOtherUser:
    async def test_users_manager_cannot_edit_an_org_admin(
        self, auth_as, make_user_session_factory, org, org_admin_id, users_manager_id
    ):
        session = _org_session(
            make_user_session_factory,
            users_manager_id,
            {org.id: (UserRole.USER, frozenset({ORG_USERS}))},
        )

        resp = await auth_as(session).patch(
            f"{USERS_BASE}/{org_admin_id}", json={"email": "takeover@example.com"}
        )

        assert resp.status_code == 403

    async def test_users_manager_can_edit_a_regular_member(
        self, auth_as, make_user_session_factory, org, member_id, users_manager_id
    ):
        session = _org_session(
            make_user_session_factory,
            users_manager_id,
            {org.id: (UserRole.USER, frozenset({ORG_USERS}))},
        )

        resp = await auth_as(session).patch(
            f"{USERS_BASE}/{member_id}", json={"firstname": "Nuevo"}
        )

        assert resp.status_code == 200

    async def test_org_admin_can_edit_a_member(
        self, auth_as, make_user_session_factory, org, org_admin_id, member_id
    ):
        session = _org_session(
            make_user_session_factory,
            org_admin_id,
            {org.id: (UserRole.ADMIN, frozenset())},
        )

        resp = await auth_as(session).patch(
            f"{USERS_BASE}/{member_id}", json={"firstname": "Nuevo"}
        )

        assert resp.status_code == 200

    async def test_member_without_users_permission_cannot_edit_others(
        self, auth_as, make_user_session_factory, org, member_id, users_manager_id
    ):
        session = _org_session(
            make_user_session_factory,
            users_manager_id,
            {org.id: (UserRole.USER, frozenset())},
        )

        resp = await auth_as(session).patch(
            f"{USERS_BASE}/{member_id}", json={"firstname": "Nuevo"}
        )

        assert resp.status_code == 403

    async def test_cannot_edit_a_user_who_also_belongs_to_another_organization(
        self, client, db_session, auth_as, make_user_session_factory, org, org_admin_id
    ):
        other_org = await add_organization(db_session)
        shared_member = await _new_user(client, db_session)
        await _add_member(db_session, shared_member, org.id, UserRole.USER)
        await _add_member(db_session, shared_member, other_org.id, UserRole.USER)
        session = _org_session(
            make_user_session_factory,
            org_admin_id,
            {org.id: (UserRole.ADMIN, frozenset())},
        )

        resp = await auth_as(session).patch(
            f"{USERS_BASE}/{shared_member}", json={"email": "x@example.com"}
        )

        assert resp.status_code == 403

    async def test_cannot_edit_a_user_from_another_organization(
        self, client, db_session, auth_as, make_user_session_factory, org, org_admin_id
    ):
        other_org = await add_organization(db_session)
        stranger = await _new_user(client, db_session)
        await _add_member(db_session, stranger, other_org.id, UserRole.USER)
        session = _org_session(
            make_user_session_factory,
            org_admin_id,
            {org.id: (UserRole.ADMIN, frozenset())},
        )

        resp = await auth_as(session).patch(
            f"{USERS_BASE}/{stranger}", json={"firstname": "X"}
        )

        assert resp.status_code == 403

    async def test_cannot_edit_global_staff(
        self, client, db_session, auth_as, make_user_session_factory, org, org_admin_id
    ):
        staff = await _new_user(client, db_session)
        db_session.add(
            RoleAssignmentModel(
                user_id=staff, role=UserRole.ADMIN, scope=UserScope.GLOBAL
            )
        )
        await _add_member(db_session, staff, org.id, UserRole.USER)
        session = _org_session(
            make_user_session_factory,
            org_admin_id,
            {org.id: (UserRole.ADMIN, frozenset())},
        )

        resp = await auth_as(session).patch(
            f"{USERS_BASE}/{staff}", json={"firstname": "X"}
        )

        assert resp.status_code == 403

    async def test_editing_a_user_closes_their_cached_session_and_refresh_token(
        self, auth_as, make_user_session_factory, org, org_admin_id, member_id
    ):
        target_session = _org_session(
            make_user_session_factory, member_id, {org.id: (UserRole.USER, frozenset())}
        )
        await redis_client.set_json(session_key(member_id), target_session)
        await AuthTokenService().generate_refresh_token(member_id)
        caller = _org_session(
            make_user_session_factory,
            org_admin_id,
            {org.id: (UserRole.ADMIN, frozenset())},
        )

        resp = await auth_as(caller).patch(
            f"{USERS_BASE}/{member_id}", json={"isActive": False}
        )

        assert resp.status_code == 200
        assert await redis_client.get(session_key(member_id)) is None
        assert await redis_client.get(f"refresh:{member_id}") is None


class TestDeleteOtherUser:
    async def test_users_manager_cannot_delete_an_org_admin_nor_the_organization(
        self,
        db_session,
        auth_as,
        make_user_session_factory,
        org,
        org_admin_id,
        users_manager_id,
    ):
        session = _org_session(
            make_user_session_factory,
            users_manager_id,
            {org.id: (UserRole.USER, frozenset({ORG_USERS}))},
        )

        resp = await auth_as(session).delete(f"{USERS_BASE}/{org_admin_id}")

        assert resp.status_code == 403
        db_session.expunge_all()
        assert await OrganizationRepository(db_session).get_by_id(org.id) is not None

    async def test_org_admin_cannot_delete_a_co_admin_nor_the_organization(
        self, client, db_session, auth_as, make_user_session_factory, org, org_admin_id
    ):
        co_admin = await _new_user(client, db_session)
        await _add_member(db_session, co_admin, org.id, UserRole.ADMIN)
        session = _org_session(
            make_user_session_factory,
            org_admin_id,
            {org.id: (UserRole.ADMIN, frozenset())},
        )

        resp = await auth_as(session).delete(f"{USERS_BASE}/{co_admin}")

        assert resp.status_code == 403
        db_session.expunge_all()
        assert await OrganizationRepository(db_session).get_by_id(org.id) is not None

    async def test_org_admin_can_delete_a_regular_member_and_closes_their_session(
        self, auth_as, make_user_session_factory, org, org_admin_id, member_id
    ):
        await redis_client.set_json(
            session_key(member_id),
            _org_session(
                make_user_session_factory,
                member_id,
                {org.id: (UserRole.USER, frozenset())},
            ),
        )
        await AuthTokenService().generate_refresh_token(member_id)
        session = _org_session(
            make_user_session_factory,
            org_admin_id,
            {org.id: (UserRole.ADMIN, frozenset())},
        )

        resp = await auth_as(session).delete(f"{USERS_BASE}/{member_id}")

        assert resp.status_code == 204
        assert await redis_client.get(session_key(member_id)) is None
        assert await redis_client.get(f"refresh:{member_id}") is None

    async def test_global_admin_deleting_an_org_admin_takes_the_organization_down(
        self, db_session, auth_as, make_user_session_factory, org, org_admin_id
    ):
        resp = await auth_as(make_user_session_factory()).delete(
            f"{USERS_BASE}/{org_admin_id}"
        )

        assert resp.status_code == 204
        db_session.expunge_all()
        assert await OrganizationRepository(db_session).get_by_id(org.id) is None


class TestMemberPermissions:
    async def test_cannot_assign_permission_to_a_non_member(
        self, client, db_session, auth_as, make_user_session_factory, org, org_admin_id
    ):
        outsider = await _new_user(client, db_session)
        session = _org_session(
            make_user_session_factory,
            org_admin_id,
            {org.id: (UserRole.ADMIN, frozenset())},
        )

        resp = await auth_as(session).put(
            f"{ORG_BASE}/{org.id}/members/{outsider}/permissions",
            json={"name": ORG_USERS, "effect": "OTORGAR"},
        )

        assert resp.status_code == 404

    async def test_assigning_a_permission_closes_the_members_cached_session(
        self, auth_as, make_user_session_factory, org, org_admin_id, member_id
    ):
        await redis_client.set_json(
            session_key(member_id),
            _org_session(
                make_user_session_factory,
                member_id,
                {org.id: (UserRole.USER, frozenset())},
            ),
        )
        session = _org_session(
            make_user_session_factory,
            org_admin_id,
            {org.id: (UserRole.ADMIN, frozenset())},
        )

        resp = await auth_as(session).put(
            f"{ORG_BASE}/{org.id}/members/{member_id}/permissions",
            json={"name": ORG_USERS, "effect": "OTORGAR"},
        )

        assert resp.status_code == 200
        assert await redis_client.get(session_key(member_id)) is None
