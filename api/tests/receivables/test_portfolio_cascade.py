"""Baja lógica de un portafolio: arrastra sus créditos y campañas, y `restore` revierte
SOLO esa cascada.

Antes `delete_portfolio` marcaba únicamente el portafolio: sus créditos seguían vivos y el
scheduler seguía disparando las campañas. El sello compartido (`deleted_at` idéntico al
del portafolio) es lo que evita que restaurar resucite créditos dados de baja antes por
otra vía (p. ej. la recarga del CSV en modo update).
"""

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from identity.organizations.repository.organization_repository import OrganizationRepository
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.campaigns.repository.campaign_time_repository import CampaignTimeRepository
from messaging.contacts.repository.contact_repository import ContactRepository
from receivables.credits.repository.credit_repository import CreditRepository
from receivables.portfolios.repository.portfolio_daily_counter_config_repository import PortfolioDailyCounterConfigRepository
from receivables.portfolios.repository.portfolio_repository import PortfolioRepository
from receivables.portfolios.repository.portfolio_user_access_repository import PortfolioUserAccessRepository
from receivables.portfolios.services.portfolio_service import PortfolioService
from tests.messaging.campaigns.conftest import build_campaign, get_channel_id
from tests.messaging.campaigns.test_campaign_time_repository import build_ct
from tests.receivables.conftest import add_organization, build_credit, build_debtor, build_portfolio


def build_service(db_session) -> PortfolioService:
    return PortfolioService(
        PortfolioRepository(db_session),
        PortfolioDailyCounterConfigRepository(db_session),
        CreditRepository(db_session),
        CampaignRepository(db_session),
        ContactRepository(db_session),
        PortfolioUserAccessRepository(db_session),
    )


async def _portfolio_with_credit_and_campaign(db_session):
    org = await add_organization(db_session)
    portfolio = build_portfolio(org.id)
    debtor = build_debtor(org.id)
    db_session.add_all([portfolio, debtor])
    await db_session.flush()
    credit = build_credit(portfolio.id, debtor.id)
    campaign = build_campaign(portfolio.id, await get_channel_id(db_session))
    db_session.add_all([credit, campaign])
    await db_session.flush()
    return org, portfolio, credit, campaign


class TestDeletePortfolioCascade:
    async def test_soft_deletes_credits_and_campaigns(self, db_session):
        _, portfolio, credit, campaign = await _portfolio_with_credit_and_campaign(db_session)

        await build_service(db_session).delete_portfolio(portfolio.id)

        assert await PortfolioRepository(db_session).get_by_id(portfolio.id) is None
        assert await CreditRepository(db_session).get_by_id(credit.id) is None
        assert await CampaignRepository(db_session).get_by_id(campaign.id) is None

    async def test_leaves_other_portfolios_untouched(self, db_session):
        org, portfolio, _, _ = await _portfolio_with_credit_and_campaign(db_session)
        other = build_portfolio(org.id)
        debtor = build_debtor(org.id)
        db_session.add_all([other, debtor])
        await db_session.flush()
        other_credit = build_credit(other.id, debtor.id)
        db_session.add(other_credit)
        await db_session.flush()

        await build_service(db_session).delete_portfolio(portfolio.id)

        assert await CreditRepository(db_session).get_by_id(other_credit.id) is not None

    async def test_deleted_campaign_is_no_longer_due_for_the_scheduler(self, db_session):
        org, portfolio, _, campaign = await _portfolio_with_credit_and_campaign(db_session)
        ct = build_ct(campaign.id, org.id)
        db_session.add(ct)
        await db_session.flush()
        now = datetime.now(timezone.utc)
        assert [d.id for d in await CampaignTimeRepository(db_session).find_due_active(now)] == [ct.id]

        await build_service(db_session).delete_portfolio(portfolio.id)

        assert await CampaignTimeRepository(db_session).find_due_active(now) == []


class TestRestorePortfolioCascade:
    async def test_restores_credits_and_campaigns_of_the_cascade(self, db_session):
        _, portfolio, credit, campaign = await _portfolio_with_credit_and_campaign(db_session)
        service = build_service(db_session)
        await service.delete_portfolio(portfolio.id)

        await service.restore_portfolio(portfolio.id)

        assert await PortfolioRepository(db_session).get_by_id(portfolio.id) is not None
        assert await CreditRepository(db_session).get_by_id(credit.id) is not None
        assert await CampaignRepository(db_session).get_by_id(campaign.id) is not None

    async def test_does_not_resurrect_a_credit_deleted_before_the_portfolio(self, db_session):
        org, portfolio, credit, _ = await _portfolio_with_credit_and_campaign(db_session)
        debtor = build_debtor(org.id)
        db_session.add(debtor)
        await db_session.flush()
        old_credit = build_credit(portfolio.id, debtor.id)
        db_session.add(old_credit)
        await db_session.flush()
        credit_repo = CreditRepository(db_session)
        await credit_repo.delete(old_credit)  # baja anterior, con su propio sello

        service = build_service(db_session)
        await service.delete_portfolio(portfolio.id)
        await service.restore_portfolio(portfolio.id)

        assert await credit_repo.get_by_id(credit.id) is not None
        assert await credit_repo.get_by_id(old_credit.id) is None

    async def test_is_blocked_while_the_organization_is_deleted(self, db_session):
        org, portfolio, _, _ = await _portfolio_with_credit_and_campaign(db_session)
        service = build_service(db_session)
        await service.delete_portfolio(portfolio.id)
        await OrganizationRepository(db_session).delete(org)

        with pytest.raises(HTTPException) as exc_info:
            await service.restore_portfolio(portfolio.id)
        assert exc_info.value.status_code == 409
