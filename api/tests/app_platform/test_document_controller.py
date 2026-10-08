import uuid

from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.schemas.user_session_schema import OrgSessionEntry
from tests.factories import get_user_by_email, register_payload

AUTH_BASE = "/api/v1/auth"
ORG_BASE = "/api/v1/organizations"

# Nota: `GET /mine`, `POST /mine/upload-ticket`, `POST /mine/{id}/confirm`,
# `GET /mine/{id}/content`, `DELETE /mine/{id}` resuelven un Deudor real detrás de la
# sesión SELF (`_require_debtor`) -- dependen de `receivables/debtors`, todavía sin
# testear. Diferidos a Fase 4. Acá solo lo que no depende de deudores.


class TestListCategories:
    """`GET /documents/categories` desapareció con la Fase 2 (separación de la
    asociación polimórfica): cada dominio expone su propio catálogo acotado. El del
    ámbito deudor (antes "identidad" vivía acá) se movió a `/debtors/me/documents`."""

    DEBTORS_ME_BASE = "/api/v1/debtors/me/documents"

    async def test_list_valid(self, auth_as, make_user_session_factory):
        authed = auth_as(make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF))
        resp = await authed.get(f"{self.DEBTORS_ME_BASE}/categories")
        assert resp.status_code == 200
        body = resp.json()
        assert any(item["value"] == "IDENTIDAD" for item in body)

    async def test_list_without_auth_returns_401(self, client):
        resp = await client.get(f"{self.DEBTORS_ME_BASE}/categories")
        assert resp.status_code == 401


class TestDownloadOrganizationDocument:
    """La descarga de un documento de organización se movió a
    `organization_controller.py` (antes vivía en el controller genérico de
    `documents`, eliminado en la Fase 2)."""

    async def test_valid(self, client, db_session, auth_as, make_user_session_factory):
        # Sube un documento real de organización (store, vía el mismo flujo que
        # organization_controller) y lo descarga desde el mismo dominio.
        payload = register_payload()
        resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
        assert resp.status_code == 201
        user = await get_user_by_email(db_session, payload["email"])
        global_admin = make_user_session_factory(user_id=user.id, role=UserRole.ADMIN, scope=UserScope.GLOBAL)
        authed = auth_as(global_admin)
        create = await authed.post(f"{ORG_BASE}/", json={"name": f"Org {uuid.uuid4().hex[:8]}", "sector": "FINTECH"})
        org_id = create.json()["id"]

        upload = await authed.patch(
            f"{ORG_BASE}/{org_id}/documents/fiscal",
            files={"file": ("fiscal.pdf", b"%PDF-1.4 contenido de prueba", "application/pdf")},
        )
        assert upload.status_code == 200
        document_id = upload.json()["fiscalDocumentFile"].split("/")[-2]

        resp = await authed.get(f"{ORG_BASE}/{org_id}/documents/{document_id}/content")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert resp.content == b"%PDF-1.4 contenido de prueba"

    async def test_not_found_returns_404(self, auth_as, make_user_session_factory):
        org_id = str(uuid.uuid4())
        authed = auth_as(
            make_user_session_factory(
                role=UserRole.ADMIN,
                scope=UserScope.ORGANIZATION,
                orgs={org_id: OrgSessionEntry(role=UserRole.ADMIN, org_name="Org", verification_status=VerificationStatus.APPROVED)},
            )
        )
        resp = await authed.get(f"{ORG_BASE}/{org_id}/documents/{uuid.uuid4()}/content")
        assert resp.status_code == 404

    async def test_forbidden_without_org_access(self, client, db_session, auth_as, make_user_session_factory):
        payload = register_payload()
        await client.post(f"{AUTH_BASE}/register/user", json=payload)
        user = await get_user_by_email(db_session, payload["email"])
        global_admin = make_user_session_factory(user_id=user.id, role=UserRole.ADMIN, scope=UserScope.GLOBAL)
        authed = auth_as(global_admin)
        create = await authed.post(f"{ORG_BASE}/", json={"name": f"Org {uuid.uuid4().hex[:8]}", "sector": "FINTECH"})
        org_id = create.json()["id"]
        upload = await authed.patch(
            f"{ORG_BASE}/{org_id}/documents/fiscal",
            files={"file": ("fiscal.pdf", b"%PDF-1.4 contenido de prueba", "application/pdf")},
        )
        document_id = upload.json()["fiscalDocumentFile"].split("/")[-2]

        unrelated = auth_as(make_user_session_factory(role=UserRole.USER, scope=UserScope.SELF))
        resp = await unrelated.get(f"{ORG_BASE}/{org_id}/documents/{document_id}/content")
        assert resp.status_code == 403
