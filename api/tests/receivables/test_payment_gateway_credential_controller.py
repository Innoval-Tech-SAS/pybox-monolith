"""Autorización de `payment-gateway-credentials`: a diferencia de `payment_methods`
(que admite un permiso delegable), estas credenciales mueven dinero real de la empresa,
así que el acceso es exclusivamente `require_org_admin` -- ni un rol no-ADMIN de la
propia organización, ni un admin de otra organización, pueden verlas ni tocarlas.
"""

import uuid

from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.schemas.user_session_schema import OrgSessionEntry
from tests.receivables.conftest import add_organization

BASE = "/api/v1/payment-gateway-credentials"


def _org_session(make_user_session_factory, org_id: uuid.UUID, role: UserRole):
    return make_user_session_factory(
        role=role,
        scope=UserScope.ORGANIZATION,
        orgs={
            str(org_id): OrgSessionEntry(
                role=role,
                org_name="Org",
                permissions=frozenset(),
                verification_status=VerificationStatus.APPROVED,
            )
        },
    )


def credential_payload(**overrides) -> dict:
    payload = {
        "provider": "WOMPI",
        "secrets": {
            "private_key": "prv_test_x",
            "events_key": "test_events_x",
            "integrity_key": "test_integrity_x",
        },
        "public_config": {"public_key": "pub_test_x"},
    }
    payload.update(overrides)
    return payload


class TestOrgAdminAccess:
    async def test_org_admin_can_create_and_list(
        self, db_session, auth_as, make_user_session_factory
    ):
        org = await add_organization(db_session)
        authed = auth_as(
            _org_session(make_user_session_factory, org.id, UserRole.ADMIN)
        )

        create_resp = await authed.post(
            f"{BASE}/?organizationId={org.id}", json=credential_payload()
        )
        assert create_resp.status_code == 201
        body = create_resp.json()
        assert body["provider"] == "WOMPI"
        assert "private_key" in body["secretKeys"]
        assert "secrets" not in body

        list_resp = await authed.get(f"{BASE}/?organizationId={org.id}")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1


class TestCrossOrganizationDenied:
    async def test_admin_of_other_org_gets_403_on_list(
        self, db_session, auth_as, make_user_session_factory
    ):
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        authed = auth_as(
            _org_session(make_user_session_factory, org_a.id, UserRole.ADMIN)
        )

        resp = await authed.get(f"{BASE}/?organizationId={org_b.id}")
        assert resp.status_code == 403

    async def test_admin_of_other_org_gets_403_on_create(
        self, db_session, auth_as, make_user_session_factory
    ):
        org_a = await add_organization(db_session)
        org_b = await add_organization(db_session)
        authed = auth_as(
            _org_session(make_user_session_factory, org_a.id, UserRole.ADMIN)
        )

        resp = await authed.post(
            f"{BASE}/?organizationId={org_b.id}", json=credential_payload()
        )
        assert resp.status_code == 403


class TestNonAdminRoleDenied:
    async def test_org_member_who_is_not_admin_gets_403(
        self, db_session, auth_as, make_user_session_factory
    ):
        """A diferencia de payment_methods (delegable por permiso), aquí ningún rol
        no-ADMIN pasa, ni siquiera con permisos asignados -- por eso ni se le da un
        `permissions` no vacío a esta sesión: no hay permiso que lo habilite."""
        org = await add_organization(db_session)
        authed = auth_as(_org_session(make_user_session_factory, org.id, UserRole.USER))

        resp = await authed.get(f"{BASE}/?organizationId={org.id}")
        assert resp.status_code == 403


class TestGlobalAdminBypass:
    async def test_global_admin_can_access_any_organization(
        self, db_session, auth_as, make_user_session_factory
    ):
        org = await add_organization(db_session)
        authed = auth_as(
            make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL)
        )

        resp = await authed.get(f"{BASE}/?organizationId={org.id}")
        assert resp.status_code == 200


class TestSingleActiveCredentialInvariant:
    """El checkout de autoservicio resuelve "la" pasarela activa de la organización sin
    que el deudor elija (ver `ReceivablesGatewayResolver.get_active_for_organization`)
    -- a lo sumo una credencial puede estar activa a la vez, sin importar la pasarela.
    """

    async def test_activating_a_second_provider_deactivates_the_first(
        self, db_session, auth_as, make_user_session_factory
    ):
        org = await add_organization(db_session)
        authed = auth_as(
            _org_session(make_user_session_factory, org.id, UserRole.ADMIN)
        )
        wompi_resp = await authed.post(
            f"{BASE}/?organizationId={org.id}",
            json=credential_payload(is_active=True),
        )
        assert wompi_resp.json()["isActive"] is True

        bold_resp = await authed.post(
            f"{BASE}/?organizationId={org.id}",
            json=credential_payload(
                provider="BOLD",
                secrets={"identity_key": "id_x", "secret_key": "sec_x"},
                public_config={},
                is_active=True,
            ),
        )
        assert bold_resp.status_code == 201
        assert bold_resp.json()["isActive"] is True

        list_resp = await authed.get(f"{BASE}/?organizationId={org.id}")
        by_provider = {row["provider"]: row["isActive"] for row in list_resp.json()}
        assert by_provider == {"WOMPI": False, "BOLD": True}

    async def test_activating_via_update_deactivates_the_others(
        self, db_session, auth_as, make_user_session_factory
    ):
        org = await add_organization(db_session)
        authed = auth_as(
            _org_session(make_user_session_factory, org.id, UserRole.ADMIN)
        )
        await authed.post(
            f"{BASE}/?organizationId={org.id}",
            json=credential_payload(is_active=True),
        )
        bold_resp = await authed.post(
            f"{BASE}/?organizationId={org.id}",
            json=credential_payload(
                provider="BOLD",
                secrets={"identity_key": "id_x", "secret_key": "sec_x"},
                public_config={},
                is_active=False,
            ),
        )
        bold_id = bold_resp.json()["id"]

        update_resp = await authed.patch(
            f"{BASE}/{bold_id}?organizationId={org.id}", json={"isActive": True}
        )
        assert update_resp.json()["isActive"] is True

        list_resp = await authed.get(f"{BASE}/?organizationId={org.id}")
        by_provider = {row["provider"]: row["isActive"] for row in list_resp.json()}
        assert by_provider == {"WOMPI": False, "BOLD": True}


class TestDuplicateProviderRejected:
    async def test_second_credential_for_same_provider_returns_409(
        self, db_session, auth_as, make_user_session_factory
    ):
        org = await add_organization(db_session)
        authed = auth_as(
            _org_session(make_user_session_factory, org.id, UserRole.ADMIN)
        )
        await authed.post(f"{BASE}/?organizationId={org.id}", json=credential_payload())

        resp = await authed.post(
            f"{BASE}/?organizationId={org.id}", json=credential_payload()
        )

        assert resp.status_code == 409
