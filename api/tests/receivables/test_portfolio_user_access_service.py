"""`PortfolioUserAccessService`: otorgar/revocar acceso a un portafolio, listar
accesos y reemplazar el set completo -- contra `db_session` real, sin mocks.

`user_id`/`granted_by` son FKs reales a `usuarios.id`: no se puede usar un
`uuid.uuid4()` inventado (viola la FK al hacer flush), hace falta un usuario
registrado de verdad -- de ahí el helper `create_user`.
"""

import pytest
from fastapi import HTTPException

from identity.organizations.models.organization_membership_model import OrganizationMembershipModel
from receivables.portfolios.services.portfolio_user_access_service import PortfolioUserAccessService
from tests.factories import get_user_by_email, register_payload
from tests.receivables.conftest import build_organization, build_portfolio

AUTH_BASE = "/api/v1/auth"


async def create_user(client, db_session):
    payload = register_payload()
    resp = await client.post(f"{AUTH_BASE}/register/user", json=payload)
    assert resp.status_code == 201
    return await get_user_by_email(db_session, payload["email"])


async def create_member(client, db_session, org_id):
    """Usuario real que además es miembro de `org_id`: los accesos solo se conceden a
    miembros de la organización."""
    user = await create_user(client, db_session)
    db_session.add(OrganizationMembershipModel(user_id=user.id, organization_id=org_id, created_by=user.id))
    await db_session.flush()
    return user


class TestGrantAccess:
    async def test_grant_creates_a_new_active_access(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user = await create_member(client, db_session, org.id)
        granter = await create_user(client, db_session)

        service = PortfolioUserAccessService(db_session)
        access = await service.grant_access(user.id, portfolio.id, org.id, granter.id)

        assert access.is_active is True
        assert access.user_id == user.id
        assert access.granted_by == granter.id

    async def test_grant_is_idempotent_for_an_already_active_access(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user = await create_member(client, db_session, org.id)
        granter_1 = await create_user(client, db_session)
        granter_2 = await create_user(client, db_session)

        service = PortfolioUserAccessService(db_session)
        first = await service.grant_access(user.id, portfolio.id, org.id, granter_1.id)
        second = await service.grant_access(user.id, portfolio.id, org.id, granter_2.id)

        assert second.id == first.id
        assert second.granted_by == granter_1.id  # no se sobrescribe: ya estaba activo

    async def test_grant_reactivates_a_revoked_access(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user = await create_member(client, db_session, org.id)
        first_granter = await create_user(client, db_session)
        new_granter = await create_user(client, db_session)

        service = PortfolioUserAccessService(db_session)
        await service.grant_access(user.id, portfolio.id, org.id, first_granter.id)
        await service.revoke_access(user.id, portfolio.id, org.id)
        reactivated = await service.grant_access(user.id, portfolio.id, org.id, new_granter.id)

        assert reactivated.is_active is True
        assert reactivated.revoked_at is None
        assert reactivated.granted_by == new_granter.id


class TestGrantAccessCrossOrgIdor:
    """Regresión: `grant_access` debe rechazar (404) un `portfolio_id` que no
    pertenece al `organization_id` dado. Antes del fix, el controller solo validaba
    que el llamante fuera admin de SU organización -- nunca que el portafolio del
    path fuera de esa misma organización -- así que un admin de la org A podía
    grabar una fila de acceso apuntando a un portafolio real de la org B."""

    async def test_portfolio_from_another_org_raises_404(self, client, db_session):
        org_a = build_organization()
        org_b = build_organization()
        db_session.add_all([org_a, org_b])
        await db_session.flush()
        portfolio_b = build_portfolio(org_b.id)
        db_session.add(portfolio_b)
        await db_session.flush()
        user = await create_member(client, db_session, org_a.id)
        granter = await create_user(client, db_session)

        service = PortfolioUserAccessService(db_session)
        with pytest.raises(HTTPException) as exc_info:
            await service.grant_access(user.id, portfolio_b.id, org_a.id, granter.id)
        assert exc_info.value.status_code == 404


class TestRevokeAccess:
    async def test_revoke_deactivates_and_stamps_revoked_at(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user = await create_member(client, db_session, org.id)
        granter = await create_user(client, db_session)

        service = PortfolioUserAccessService(db_session)
        await service.grant_access(user.id, portfolio.id, org.id, granter.id)
        await service.revoke_access(user.id, portfolio.id, org.id)

        accesses = await service.get_user_portfolios(user.id, org.id)
        assert accesses == []

    async def test_revoke_without_existing_access_is_a_noop(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        user = await create_member(client, db_session, org.id)
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()

        service = PortfolioUserAccessService(db_session)
        # No debe lanzar excepción aunque no exista el acceso.
        await service.revoke_access(user.id, portfolio.id, org.id)


class TestRevokeAllForUserInOrg:
    async def test_revokes_every_active_access_in_the_org(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio_a = build_portfolio(org.id)
        portfolio_b = build_portfolio(org.id)
        db_session.add_all([portfolio_a, portfolio_b])
        await db_session.flush()
        user = await create_member(client, db_session, org.id)
        granter = await create_user(client, db_session)

        service = PortfolioUserAccessService(db_session)
        await service.grant_access(user.id, portfolio_a.id, org.id, granter.id)
        await service.grant_access(user.id, portfolio_b.id, org.id, granter.id)

        await service.revoke_all_for_user_in_org(user.id, org.id)

        assert await service.get_user_portfolios(user.id, org.id) == []


class TestListOrgPortfoliosWithAccessStatus:
    async def test_flags_which_portfolios_are_granted(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio_a = build_portfolio(org.id)
        portfolio_b = build_portfolio(org.id)
        db_session.add_all([portfolio_a, portfolio_b])
        await db_session.flush()
        user = await create_member(client, db_session, org.id)
        granter = await create_user(client, db_session)

        service = PortfolioUserAccessService(db_session)
        await service.grant_access(user.id, portfolio_a.id, org.id, granter.id)

        result = await service.list_org_portfolios_with_access_status(user.id, org.id)
        status_by_id = {pid: granted for pid, _name, granted in result}

        assert status_by_id[portfolio_a.id] is True
        assert status_by_id[portfolio_b.id] is False


class TestReplaceAccess:
    async def test_replace_grants_new_and_revokes_missing(self, client, db_session):
        org = build_organization()
        db_session.add(org)
        await db_session.flush()
        portfolio = build_portfolio(org.id)
        db_session.add(portfolio)
        await db_session.flush()
        user_a = await create_member(client, db_session, org.id)
        user_b = await create_member(client, db_session, org.id)
        granter = await create_user(client, db_session)

        service = PortfolioUserAccessService(db_session)
        await service.grant_access(user_a.id, portfolio.id, org.id, granter.id)

        result = await service.replace_access(portfolio.id, org.id, [user_b.id], granter.id)

        assert {a.user_id for a in result} == {user_b.id}
        remaining = await service.list_portfolio_access(portfolio.id)
        active_user_ids = {a.user_id for a in remaining if a.is_active}
        assert active_user_ids == {user_b.id}
