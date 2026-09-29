import uuid

import pytest
from fastapi import HTTPException

from messaging.provider_credentials.enums.provider_credential_enums import MessagingCredentialProvider
from messaging.provider_credentials.schemas.provider_credential_schemas import MessagingProviderCredentialUpsert
from messaging.provider_credentials.services.provider_credential_admin_service import (
    MessagingProviderCredentialAdminService,
)
from messaging.provider_credentials.services.provider_credential_service import MessagingProviderCredentialService
from identity.users.enums.user_enums import UserRole, UserScope

BASE = "/api/v1/admin/messaging-credentials"


def credential_payload(**overrides) -> dict:
    payload = {
        "country_code": None,
        "provider": "WHATSAPP_CLOUD",
        "secrets": {"access_token": "shhh", "app_secret": "shhh2"},
        "public_config": {"waba_id": "waba-123"},
    }
    payload.update(overrides)
    return payload


class TestListCredentials:
    async def test_list_valid_as_global_admin(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.get(BASE)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_list_without_global_admin_returns_403(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF))
        resp = await authed.get(BASE)
        assert resp.status_code == 403

    async def test_list_without_auth_returns_401(self, client):
        resp = await client.get(BASE)
        assert resp.status_code == 401


class TestUpsertCredential:
    async def test_upsert_valid(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.put(BASE, json=credential_payload())
        assert resp.status_code == 200
        body = resp.json()
        assert body["provider"] == "WHATSAPP_CLOUD"
        assert "access_token" in body["secretKeys"]
        assert "secrets" not in body

    async def test_upsert_invalid_provider_returns_422(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        resp = await authed.put(BASE, json=credential_payload(provider="unknown_provider"))
        assert resp.status_code == 422

    async def test_upsert_without_global_admin_returns_403(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF))
        resp = await authed.put(BASE, json=credential_payload())
        assert resp.status_code == 403


class TestDeleteCredential:
    async def test_delete_valid(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        upsert = await authed.put(BASE, json=credential_payload(country_code="CO", provider="360NRS_SMS", secrets={"token": "x"}))
        credential_id = upsert.json()["id"]
        resp = await authed.delete(f"{BASE}/{credential_id}")
        assert resp.status_code == 204

    async def test_delete_without_global_admin_returns_403(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF))
        resp = await authed.delete(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Servicios directos (sin HTTP): resolución país→global, descifrado y el merge de
# secretos en upserts sucesivos -- lógica que el controller no ejercita directo.
# ---------------------------------------------------------------------------


class TestMessagingProviderCredentialAdminServiceUpsertMerge:
    async def test_second_upsert_without_secrets_preserves_existing_ones(self, db_session):
        admin_service = MessagingProviderCredentialAdminService(db_session)
        first = await admin_service.upsert(
            MessagingProviderCredentialUpsert(
                country_code="CO",
                provider=MessagingCredentialProvider.NRS360_SMS,
                secrets={"token": "secreto-original"},
                public_config={"sender": "pybox"},
            )
        )
        assert first.secret_keys == ["token"]

        # Segundo upsert edita solo public_config, sin reenviar secretos: deben
        # conservarse los ya guardados en vez de perderse.
        second = await admin_service.upsert(
            MessagingProviderCredentialUpsert(
                country_code="CO",
                provider=MessagingCredentialProvider.NRS360_SMS,
                secrets={},
                public_config={"sender": "pybox-actualizado"},
            )
        )
        assert second.id == first.id
        assert second.secret_keys == ["token"]
        assert second.public_config["sender"] == "pybox-actualizado"

        credential_service = MessagingProviderCredentialService(db_session)
        decrypted = await credential_service.get_decrypted("CO", MessagingCredentialProvider.NRS360_SMS)
        assert decrypted.get("token") == "secreto-original"

    async def test_second_upsert_with_new_secret_rotates_it(self, db_session):
        admin_service = MessagingProviderCredentialAdminService(db_session)
        await admin_service.upsert(
            MessagingProviderCredentialUpsert(
                country_code="MX",
                provider=MessagingCredentialProvider.NRS360_SMS,
                secrets={"token": "vieja"},
            )
        )
        await admin_service.upsert(
            MessagingProviderCredentialUpsert(
                country_code="MX",
                provider=MessagingCredentialProvider.NRS360_SMS,
                secrets={"token": "nueva"},
            )
        )
        credential_service = MessagingProviderCredentialService(db_session)
        decrypted = await credential_service.get_decrypted("MX", MessagingCredentialProvider.NRS360_SMS)
        assert decrypted.get("token") == "nueva"


class TestMessagingProviderCredentialServiceResolution:
    async def test_country_specific_credential_takes_priority_over_global(self, db_session):
        admin_service = MessagingProviderCredentialAdminService(db_session)
        await admin_service.upsert(
            MessagingProviderCredentialUpsert(
                country_code=None,
                provider=MessagingCredentialProvider.NRS360_EMAIL,
                secrets={"token": "global-token"},
            )
        )
        await admin_service.upsert(
            MessagingProviderCredentialUpsert(
                country_code="AR",
                provider=MessagingCredentialProvider.NRS360_EMAIL,
                secrets={"token": "ar-token"},
            )
        )

        credential_service = MessagingProviderCredentialService(db_session)
        ar_credential = await credential_service.get_decrypted("AR", MessagingCredentialProvider.NRS360_EMAIL)
        assert ar_credential.get("token") == "ar-token"

    async def test_falls_back_to_global_when_no_country_specific_credential(self, db_session):
        admin_service = MessagingProviderCredentialAdminService(db_session)
        await admin_service.upsert(
            MessagingProviderCredentialUpsert(
                country_code=None,
                provider=MessagingCredentialProvider.NRS360_SMS,
                secrets={"token": "global-sms-token"},
            )
        )
        credential_service = MessagingProviderCredentialService(db_session)
        result = await credential_service.get_decrypted("PE", MessagingCredentialProvider.NRS360_SMS)
        assert result is not None
        assert result.get("token") == "global-sms-token"

    async def test_returns_none_when_no_credential_configured(self, db_session):
        credential_service = MessagingProviderCredentialService(db_session)
        result = await credential_service.get_decrypted("ZZ", MessagingCredentialProvider.WHATSAPP_CLOUD)
        assert result is None

    async def test_inactive_credential_is_not_resolved(self, db_session):
        admin_service = MessagingProviderCredentialAdminService(db_session)
        await admin_service.upsert(
            MessagingProviderCredentialUpsert(
                country_code="VE",
                provider=MessagingCredentialProvider.WHATSAPP_CLOUD,
                secrets={"access_token": "x", "app_secret": "y"},
                is_active=False,
            )
        )
        credential_service = MessagingProviderCredentialService(db_session)
        result = await credential_service.get_decrypted("VE", MessagingCredentialProvider.WHATSAPP_CLOUD)
        assert result is None

    async def test_resolve_by_lookup_key(self, db_session):
        admin_service = MessagingProviderCredentialAdminService(db_session)
        await admin_service.upsert(
            MessagingProviderCredentialUpsert(
                country_code=None,
                provider=MessagingCredentialProvider.WHATSAPP_CLOUD,
                secrets={"access_token": "x", "app_secret": "y"},
                lookup_key="waba-12345",
            )
        )
        credential_service = MessagingProviderCredentialService(db_session)
        result = await credential_service.resolve_by_lookup_key(MessagingCredentialProvider.WHATSAPP_CLOUD, "waba-12345")
        assert result is not None
        assert result.lookup_key == "waba-12345"

    async def test_resolve_by_unknown_lookup_key_returns_none(self, db_session):
        credential_service = MessagingProviderCredentialService(db_session)
        result = await credential_service.resolve_by_lookup_key(MessagingCredentialProvider.WHATSAPP_CLOUD, "no-existe")
        assert result is None


class TestMessagingProviderCredentialAdminServiceDelete:
    async def test_delete_unknown_id_raises_404(self, db_session):
        admin_service = MessagingProviderCredentialAdminService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await admin_service.delete(uuid.uuid4())
        assert exc_info.value.status_code == 404
