"""`/internal/debtor-identity/*` lo consume n8n sin sesión de usuario: sin la llave de servicio
no se responde nada, porque leen deudores de cualquier organización.
"""

import pytest

from receivables.contact_methods.enums.contact_method_enums import ContactMethodType
from receivables.contact_methods.models.contact_method_model import ContactMethodModel
from tests.factories import unique_document_number
from tests.receivables.conftest import add_organization, build_debtor

CHALLENGE_URL = "/api/v1/internal/debtor-identity/challenge"
VERIFY_URL = "/api/v1/internal/debtor-identity/verify"
KEY = "llave-de-prueba"


async def add_debtor_with_email(db_session, email="persona@correo.com"):
    org = await add_organization(db_session)
    doc = unique_document_number()
    debtor = build_debtor(org.id, document_number_plain=doc)
    db_session.add(debtor)
    await db_session.flush()
    db_session.add(
        ContactMethodModel(
            contact_type=ContactMethodType.EMAIL,
            contact_value=email,
            debtor_id=debtor.id,
        )
    )
    await db_session.flush()
    return doc


class TestServiceKeyAuthentication:
    @pytest.mark.parametrize("url", [CHALLENGE_URL, VERIFY_URL])
    async def test_without_key_is_rejected(self, client, monkeypatch, url):
        monkeypatch.setenv("N8N_SERVICE_KEY", KEY)

        resp = await client.post(
            url,
            json={
                "documentType": "CC",
                "documentNumber": "1",
                "channel": "EMAIL",
                "value": "a@b.co",
            },
        )

        assert resp.status_code == 401

    @pytest.mark.parametrize("url", [CHALLENGE_URL, VERIFY_URL])
    async def test_wrong_key_is_rejected(self, client, monkeypatch, url):
        monkeypatch.setenv("N8N_SERVICE_KEY", KEY)

        resp = await client.post(
            url,
            headers={"X-Service-Key": "otra"},
            json={
                "documentType": "CC",
                "documentNumber": "1",
                "channel": "EMAIL",
                "value": "a@b.co",
            },
        )

        assert resp.status_code == 401

    @pytest.mark.parametrize("url", [CHALLENGE_URL, VERIFY_URL])
    async def test_rejects_everything_when_the_key_is_not_configured(
        self, client, monkeypatch, url
    ):
        monkeypatch.delenv("N8N_SERVICE_KEY", raising=False)

        resp = await client.post(
            url,
            headers={"X-Service-Key": KEY},
            json={
                "documentType": "CC",
                "documentNumber": "1",
                "channel": "EMAIL",
                "value": "a@b.co",
            },
        )

        assert resp.status_code == 401

    async def test_empty_configured_key_does_not_accept_an_empty_header(
        self, client, monkeypatch
    ):
        monkeypatch.setenv("N8N_SERVICE_KEY", "")

        resp = await client.post(
            CHALLENGE_URL,
            headers={"X-Service-Key": ""},
            json={"documentType": "CC", "documentNumber": "1"},
        )

        assert resp.status_code == 401

    async def test_a_user_session_alone_is_not_enough(self, client, monkeypatch):
        """Las cookies de un usuario logueado no sustituyen la llave de servicio."""
        monkeypatch.setenv("N8N_SERVICE_KEY", KEY)

        resp = await client.post(
            CHALLENGE_URL, json={"documentType": "CC", "documentNumber": "1"}
        )

        assert resp.status_code == 401


class TestEndpoints:
    async def test_challenge_returns_only_the_masked_hint(
        self, client, db_session, monkeypatch
    ):
        monkeypatch.setenv("N8N_SERVICE_KEY", KEY)
        doc = await add_debtor_with_email(db_session, "dev.innovaltect@gmail.com")

        resp = await client.post(
            CHALLENGE_URL,
            headers={"X-Service-Key": KEY},
            json={"documentType": "CC", "documentNumber": doc},
        )

        assert resp.status_code == 200
        assert resp.json() == {
            "available": True,
            "channel": "EMAIL",
            "hint": "de*************@*****.com",
        }

    async def test_challenge_for_unknown_document_is_a_plain_200(
        self, client, monkeypatch
    ):
        monkeypatch.setenv("N8N_SERVICE_KEY", KEY)

        resp = await client.post(
            CHALLENGE_URL,
            headers={"X-Service-Key": KEY},
            json={"documentType": "CC", "documentNumber": unique_document_number()},
        )

        assert resp.status_code == 200
        assert resp.json() == {"available": False, "channel": None, "hint": None}

    async def test_verify_answers_true_and_false(self, client, db_session, monkeypatch):
        monkeypatch.setenv("N8N_SERVICE_KEY", KEY)
        doc = await add_debtor_with_email(db_session, "persona@correo.com")
        headers = {"X-Service-Key": KEY}

        ok = await client.post(
            VERIFY_URL,
            headers=headers,
            json={
                "documentType": "CC",
                "documentNumber": doc,
                "channel": "EMAIL",
                "value": "persona@correo.com",
            },
        )
        bad = await client.post(
            VERIFY_URL,
            headers=headers,
            json={
                "documentType": "CC",
                "documentNumber": doc,
                "channel": "EMAIL",
                "value": "otra@correo.com",
            },
        )

        assert ok.json() == {"verified": True}
        assert bad.json() == {"verified": False}

    async def test_verify_is_rate_limited_per_document(
        self, client, db_session, monkeypatch
    ):
        monkeypatch.setenv("N8N_SERVICE_KEY", KEY)
        doc = await add_debtor_with_email(db_session)
        body = {
            "documentType": "CC",
            "documentNumber": doc,
            "channel": "EMAIL",
            "value": "mal@correo.com",
        }

        statuses = [
            (
                await client.post(VERIFY_URL, headers={"X-Service-Key": KEY}, json=body)
            ).status_code
            for _ in range(6)
        ]

        assert statuses == [200, 200, 200, 200, 200, 429]

    async def test_invalid_document_type_is_a_validation_error(
        self, client, monkeypatch
    ):
        monkeypatch.setenv("N8N_SERVICE_KEY", KEY)

        resp = await client.post(
            CHALLENGE_URL,
            headers={"X-Service-Key": KEY},
            json={"documentType": "NOPE", "documentNumber": "1"},
        )

        assert resp.status_code == 422

    async def test_endpoints_are_not_published_in_openapi(self, client):
        schema = (
            (await client.get("/openapi.json")).json()
            if (await client.get("/openapi.json")).status_code == 200
            else {"paths": {}}
        )

        assert not any(
            "/internal/debtor-identity" in path for path in schema.get("paths", {})
        )
