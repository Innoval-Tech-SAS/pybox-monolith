import uuid

from sqlalchemy import select

from identity.organizations.enums.organization_enums import VerificationStatus
from identity.users.enums.user_enums import UserRole, UserScope
from identity.users.schemas.user_session_schema import OrgSessionEntry
from receivables.portfolios.models.portfolio_model import PortfolioModel
from tests.receivables.conftest import build_organization, build_portfolio, build_portfolio_csv, portfolio_csv_row

BASE = "/api/v1/portfolios"


def org_member_session(
    make_user_session_factory, user_id, org_id, role=UserRole.USER, permissions=frozenset({"portfolio.upload_new"})
):
    return make_user_session_factory(
        user_id=user_id,
        role=role,
        scope=UserScope.ORGANIZATION,
        orgs={
            org_id: OrgSessionEntry(
                role=role, org_name="Org", verification_status=VerificationStatus.APPROVED, permissions=permissions
            )
        },
    )


class TestCsvTemplates:
    async def test_portfolio_template_valid(self, client):
        resp = await client.get(f"{BASE}/upload-csv/template")
        assert resp.status_code == 200
        assert "Numero de documento" in resp.text

    async def test_installments_template_valid(self, client):
        resp = await client.get(f"{BASE}/upload-csv/installments/template")
        assert resp.status_code == 200
        assert "Numero de credito" in resp.text


class TestUploadCsv:
    async def test_valid_creates_portfolio_and_credit(
        self, client, db_session, auth_as, make_user_session_factory, verified_org_id, real_admin_user_id
    ):
        session = org_member_session(make_user_session_factory, real_admin_user_id, verified_org_id)
        authed = auth_as(session)
        csv_bytes = build_portfolio_csv([portfolio_csv_row()])
        resp = await authed.post(
            f"{BASE}/upload-csv",
            params={"organizationId": verified_org_id, "portfolioName": "Portafolio CSV"},
            files={"file": ("cartera.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 202

        portfolio = (
            await db_session.execute(
                select(PortfolioModel).where(PortfolioModel.organization_id == uuid.UUID(verified_org_id))
            )
        ).scalars().first()
        assert portfolio is not None
        assert portfolio.name == "Portafolio CSV"

        # La sesión org-member que subió el CSV no tiene acceso al portfolio en sí
        # (son cosas distintas: pertenecer a la org vs. tener el grant de portfolio) --
        # se verifica con un admin global aparte.
        global_admin = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        stats = await global_admin.get(f"{BASE}/{portfolio.id}/stats")
        assert stats.status_code == 200
        assert stats.json()["creditos"] == 1

    async def test_invalid_extension_returns_400(
        self, auth_as, make_user_session_factory, verified_org_id, real_admin_user_id
    ):
        session = org_member_session(make_user_session_factory, real_admin_user_id, verified_org_id)
        authed = auth_as(session)
        resp = await authed.post(
            f"{BASE}/upload-csv",
            params={"organizationId": verified_org_id},
            files={"file": ("cartera.txt", b"contenido", "text/plain")},
        )
        assert resp.status_code == 400

    async def test_unverified_org_returns_403(
        self, client, db_session, auth_as, make_user_session_factory, real_admin_user_id
    ):
        from identity.organizations.models.organization_model import OrganizationModel

        payload_org = {"name": f"Org sin verificar {uuid.uuid4().hex[:8]}", "sector": "FINTECH"}
        global_admin = auth_as(make_user_session_factory(user_id=real_admin_user_id, role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        create = await global_admin.post("/api/v1/organizations/", json=payload_org)
        assert create.status_code == 201
        org_id = create.json()["id"]
        # No se aprueba (queda PENDING) a propósito.

        session = org_member_session(make_user_session_factory, real_admin_user_id, org_id)
        authed = auth_as(session)
        csv_bytes = build_portfolio_csv([portfolio_csv_row()])
        resp = await authed.post(
            f"{BASE}/upload-csv",
            params={"organizationId": org_id},
            files={"file": ("cartera.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 403

    async def test_without_org_access_returns_403(
        self, auth_as, make_user_session_factory, verified_org_id, real_admin_user_id
    ):
        unrelated = auth_as(make_user_session_factory(user_id=real_admin_user_id, role=UserRole.USER, scope=UserScope.SELF))
        csv_bytes = build_portfolio_csv([portfolio_csv_row()])
        resp = await unrelated.post(
            f"{BASE}/upload-csv",
            params={"organizationId": verified_org_id},
            files={"file": ("cartera.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 403

    async def test_without_auth_returns_401(self, client):
        resp = await client.post(f"{BASE}/upload-csv", files={"file": ("cartera.csv", b"x", "text/csv")})
        assert resp.status_code == 401


class TestUploadCsvAppend:
    async def test_valid_adds_credit_to_existing_portfolio(
        self, client, db_session, auth_as, make_user_session_factory, real_portfolio, real_admin_user_id
    ):
        org_id = str(real_portfolio.organization_id)
        session = make_user_session_factory(
            user_id=real_admin_user_id,
            role=UserRole.ADMIN,
            scope=UserScope.ORGANIZATION,
            orgs={org_id: OrgSessionEntry(
                role=UserRole.ADMIN, org_name="Org",
                verification_status=VerificationStatus.APPROVED,
                permissions=frozenset({"portfolio.upload_new", "portfolio.upload_update"}),
            )},
        )
        authed = auth_as(session)
        csv_bytes = build_portfolio_csv([portfolio_csv_row()])
        resp = await authed.post(
            f"{BASE}/upload-csv/append",
            params={"portfolioId": str(real_portfolio.id)},
            files={"file": ("cartera.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 202

        global_admin = auth_as(make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL))
        stats = await global_admin.get(f"{BASE}/{real_portfolio.id}/stats")
        assert stats.json()["creditos"] == 1

    async def test_without_upload_permission_returns_403(
        self, auth_as, make_user_session_factory, real_portfolio, real_admin_user_id
    ):
        org_id = str(real_portfolio.organization_id)
        session = make_user_session_factory(
            user_id=real_admin_user_id,
            role=UserRole.USER,
            scope=UserScope.ORGANIZATION,
            orgs={org_id: OrgSessionEntry(role=UserRole.USER, org_name="Org", verification_status=VerificationStatus.APPROVED)},
        )
        authed = auth_as(session)
        csv_bytes = build_portfolio_csv([portfolio_csv_row()])
        resp = await authed.post(
            f"{BASE}/upload-csv/append",
            params={"portfolioId": str(real_portfolio.id)},
            files={"file": ("cartera.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 403

    async def test_unverified_org_returns_403(
        self, db_session, auth_as, make_user_session_factory, real_admin_user_id
    ):
        """Regresión para la Fase 3c de la auditoría: `upload_csv_append` pasó de
        instanciar `OrganizationRepository` directo a usar
        `OrganizationService.ensure_verified` -- este test confirma que el gate de
        organización no verificada sigue funcionando igual tras ese cambio."""
        org = build_organization(verification_status=VerificationStatus.PENDING)
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()

        session = make_user_session_factory(
            user_id=real_admin_user_id,
            role=UserRole.USER,
            scope=UserScope.ORGANIZATION,
            orgs={str(org.id): OrgSessionEntry(
                role=UserRole.USER, org_name="Org",
                verification_status=VerificationStatus.PENDING,
                permissions=frozenset({"portfolio.upload_new", "portfolio.upload_update"}),
            )},
        )
        authed = auth_as(session)
        csv_bytes = build_portfolio_csv([portfolio_csv_row()])
        resp = await authed.post(
            f"{BASE}/upload-csv/append",
            params={"portfolioId": str(portfolio.id)},
            files={"file": ("cartera.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 403


class TestUploadCsvUpdate:
    async def test_valid_replaces_credits(
        self, client, db_session, auth_as, make_user_session_factory, real_credit, real_admin_user_id
    ):
        portfolio_id = real_credit.portfolio_id
        session = make_user_session_factory(user_id=real_admin_user_id, role=UserRole.ADMIN, scope=UserScope.GLOBAL)
        authed = auth_as(session)
        csv_bytes = build_portfolio_csv([portfolio_csv_row()])
        resp = await authed.post(
            f"{BASE}/upload-csv/update",
            params={"portfolioId": str(portfolio_id)},
            files={"file": ("cartera.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 202

        stats = await authed.get(f"{BASE}/{portfolio_id}/stats")
        # el update reemplaza: el crédito original desapareció, el nuevo del CSV quedó.
        assert stats.json()["creditos"] == 1

    async def test_from_an_unrelated_org_returns_404(
        self, auth_as, make_user_session_factory, real_credit, real_admin_user_id
    ):
        org_id = str(real_credit.portfolio_id)
        session = make_user_session_factory(
            user_id=real_admin_user_id,
            role=UserRole.USER,
            scope=UserScope.ORGANIZATION,
            orgs={str(uuid.uuid4()): OrgSessionEntry(role=UserRole.USER, org_name="Otra", verification_status=VerificationStatus.APPROVED)},
        )
        authed = auth_as(session)
        csv_bytes = build_portfolio_csv([portfolio_csv_row()])
        resp = await authed.post(
            f"{BASE}/upload-csv/update",
            params={"portfolioId": str(real_credit.portfolio_id)},
            files={"file": ("cartera.csv", csv_bytes, "text/csv")},
        )
        # No pertenece a la organización dueña: 404, igual que un portafolio inexistente.
        assert resp.status_code == 404

    async def test_unverified_org_returns_403(self, db_session, auth_as, make_user_session_factory):
        """Regresión para la Fase 3c: `upload_csv_update` también pasó a usar
        `OrganizationService.ensure_verified` en vez de `OrganizationRepository`
        directo."""
        org = build_organization(verification_status=VerificationStatus.PENDING)
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()

        session = make_user_session_factory(role=UserRole.ADMIN, scope=UserScope.GLOBAL)
        authed = auth_as(session)
        csv_bytes = build_portfolio_csv([portfolio_csv_row()])
        resp = await authed.post(
            f"{BASE}/upload-csv/update",
            params={"portfolioId": str(portfolio.id)},
            files={"file": ("cartera.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 403
