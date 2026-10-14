"""Tests de `CampaignRepository` contra la base de datos real (sin mocks):
`db_session` corre en una transacción por test que se revierte sola (ver
tests/conftest.py). Cubre las queries reales: paginación+búsqueda, soft-delete
implícito en `list_by_portfolio`/`get_by_id_and_portfolio`, `get_or_create_manual`
(idempotencia) y el filtro cross-organización de `get_by_id_and_organization_id`.
"""

import uuid

from messaging.campaigns.enums.campaign_enums import CampaignStatus
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.channels.enums.channel_enums import ChannelName
from tests.messaging.campaigns.conftest import build_campaign, get_channel_id
from tests.receivables.conftest import build_organization, build_portfolio


async def _setup_portfolio(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    return org, portfolio


class TestListByPortfolio:
    async def test_only_lists_campaigns_of_given_portfolio(self, db_session):
        _org, portfolio_a = await _setup_portfolio(db_session)
        _org_b, portfolio_b = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session)

        db_session.add(build_campaign(portfolio_a.id, channel_id, name="Campaña A"))
        db_session.add(build_campaign(portfolio_b.id, channel_id, name="Campaña B"))
        await db_session.flush()

        repo = CampaignRepository(db_session)
        campaigns, total = await repo.list_by_portfolio(
            portfolio_a.id, page=1, page_size=10
        )

        assert total == 1
        assert [c.name for c in campaigns] == ["Campaña A"]

    async def test_soft_deleted_campaigns_are_excluded(self, db_session):
        _org, portfolio = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session)
        visible = build_campaign(portfolio.id, channel_id, name="Visible")
        deleted = build_campaign(portfolio.id, channel_id, name="Borrada")
        db_session.add_all([visible, deleted])
        await db_session.flush()

        repo = CampaignRepository(db_session)
        await repo.delete(deleted)

        campaigns, total = await repo.list_by_portfolio(
            portfolio.id, page=1, page_size=10
        )
        assert total == 1
        assert [c.name for c in campaigns] == ["Visible"]

    async def test_search_filters_by_name_case_insensitive(self, db_session):
        _org, portfolio = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session)
        db_session.add_all(
            [
                build_campaign(portfolio.id, channel_id, name="Recordatorio de pago"),
                build_campaign(portfolio.id, channel_id, name="Promoción especial"),
            ]
        )
        await db_session.flush()

        repo = CampaignRepository(db_session)
        campaigns, total = await repo.list_by_portfolio(
            portfolio.id, page=1, page_size=10, search="recordatorio"
        )

        assert total == 1
        assert campaigns[0].name == "Recordatorio de pago"

    async def test_pagination_respects_page_and_page_size(self, db_session):
        _org, portfolio = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session)
        for i in range(5):
            db_session.add(
                build_campaign(portfolio.id, channel_id, name=f"Campaña {i:02d}")
            )
        await db_session.flush()

        repo = CampaignRepository(db_session)
        page1, total = await repo.list_by_portfolio(
            portfolio.id, page=1, page_size=2, sort_by="name", sort_order="asc"
        )
        page2, _ = await repo.list_by_portfolio(
            portfolio.id, page=2, page_size=2, sort_by="name", sort_order="asc"
        )

        assert total == 5
        assert len(page1) == 2
        assert len(page2) == 2
        assert {c.id for c in page1}.isdisjoint({c.id for c in page2})

    async def test_sort_order_desc_reverses_results(self, db_session):
        _org, portfolio = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session)
        db_session.add_all(
            [
                build_campaign(portfolio.id, channel_id, name="A primera"),
                build_campaign(portfolio.id, channel_id, name="Z ultima"),
            ]
        )
        await db_session.flush()

        repo = CampaignRepository(db_session)
        campaigns, _ = await repo.list_by_portfolio(
            portfolio.id, page=1, page_size=10, sort_by="name", sort_order="desc"
        )

        assert [c.name for c in campaigns] == ["Z ultima", "A primera"]


class TestGetByIdAndPortfolio:
    async def test_returns_none_for_unknown_campaign(self, db_session):
        repo = CampaignRepository(db_session)
        assert await repo.get_by_id_and_portfolio(uuid.uuid4(), uuid.uuid4()) is None

    async def test_returns_none_when_campaign_belongs_to_other_portfolio(
        self, db_session
    ):
        _org, portfolio_a = await _setup_portfolio(db_session)
        _org_b, portfolio_b = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session)
        campaign = build_campaign(portfolio_a.id, channel_id)
        db_session.add(campaign)
        await db_session.flush()

        repo = CampaignRepository(db_session)
        assert await repo.get_by_id_and_portfolio(campaign.id, portfolio_b.id) is None

    async def test_returns_none_for_soft_deleted_campaign(self, db_session):
        _org, portfolio = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session)
        campaign = build_campaign(portfolio.id, channel_id)
        db_session.add(campaign)
        await db_session.flush()

        repo = CampaignRepository(db_session)
        await repo.delete(campaign)

        assert await repo.get_by_id_and_portfolio(campaign.id, portfolio.id) is None


class TestGetOrCreateManual:
    async def test_creates_manual_campaign_when_none_exists(self, db_session):
        _org, portfolio = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session, ChannelName.EMAIL)

        repo = CampaignRepository(db_session)
        campaign = await repo.get_or_create_manual(portfolio.id, channel_id, "Email")

        assert campaign.description == "__manual__"
        assert campaign.status == CampaignStatus.DRAFT
        assert "Email" in campaign.name

    async def test_second_call_reuses_the_same_manual_campaign(self, db_session):
        _org, portfolio = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session, ChannelName.EMAIL)

        repo = CampaignRepository(db_session)
        first = await repo.get_or_create_manual(portfolio.id, channel_id, "Email")
        second = await repo.get_or_create_manual(portfolio.id, channel_id, "Email")

        assert first.id == second.id

    async def test_different_channels_get_separate_manual_campaigns(self, db_session):
        _org, portfolio = await _setup_portfolio(db_session)
        email_channel_id = await get_channel_id(db_session, ChannelName.EMAIL)
        sms_channel_id = await get_channel_id(db_session, ChannelName.SMS)

        repo = CampaignRepository(db_session)
        email_campaign = await repo.get_or_create_manual(
            portfolio.id, email_channel_id, "Email"
        )
        sms_campaign = await repo.get_or_create_manual(
            portfolio.id, sms_channel_id, "SMS"
        )

        assert email_campaign.id != sms_campaign.id


class TestGetByIdAndOrganizationId:
    async def test_finds_campaign_via_portfolio_organization(self, db_session):
        org, portfolio = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session)
        campaign = build_campaign(portfolio.id, channel_id)
        db_session.add(campaign)
        await db_session.flush()

        repo = CampaignRepository(db_session)
        found = await repo.get_by_id_and_organization_id(campaign.id, org.id)

        assert found is not None
        assert found.id == campaign.id

    async def test_returns_none_for_campaign_of_different_organization(
        self, db_session
    ):
        _org_a, portfolio_a = await _setup_portfolio(db_session)
        org_b, _portfolio_b = await _setup_portfolio(db_session)
        channel_id = await get_channel_id(db_session)
        campaign = build_campaign(portfolio_a.id, channel_id)
        db_session.add(campaign)
        await db_session.flush()

        repo = CampaignRepository(db_session)
        assert await repo.get_by_id_and_organization_id(campaign.id, org_b.id) is None


class TestListByOrganizationId:
    async def test_lists_campaigns_across_portfolios_of_same_org_sorted_by_name(
        self, db_session
    ):
        org, portfolio_1 = await _setup_portfolio(db_session)
        portfolio_2 = build_portfolio(org.id)
        db_session.add(portfolio_2)
        await db_session.flush()
        channel_id = await get_channel_id(db_session)

        db_session.add_all(
            [
                build_campaign(portfolio_1.id, channel_id, name="Z campaña"),
                build_campaign(portfolio_2.id, channel_id, name="A campaña"),
            ]
        )
        await db_session.flush()

        repo = CampaignRepository(db_session)
        campaigns = await repo.list_by_organization_id(org.id)

        assert [c.name for c in campaigns] == ["A campaña", "Z campaña"]
