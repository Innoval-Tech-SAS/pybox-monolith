"""Tests de `CampaignTimeRepository` contra la base de datos real (sin mocks). El
riesgo real de estas queries: `find_due_active` es la que usa el cron para decidir
qué campañas procesar en cada tick (no debe traer campañas futuras, inactivas, ni
de campañas soft-deleted), y `list_active_by_org` es la que arma la línea de
tiempo (debe hacer el join correcto campaña<->programación).
"""

import uuid
from datetime import datetime, timedelta, timezone

from messaging.campaigns.models.campaign_time_model import CampaignTimeModel
from messaging.campaigns.repository.campaign_repository import CampaignRepository
from messaging.campaigns.repository.campaign_time_repository import CampaignTimeRepository
from tests.messaging.campaigns.conftest import build_campaign, get_channel_id
from tests.receivables.conftest import build_organization, build_portfolio


async def _setup_campaign(db_session, **overrides):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    channel_id = await get_channel_id(db_session)
    campaign = build_campaign(portfolio.id, channel_id, **overrides)
    db_session.add(campaign)
    await db_session.flush()
    return org, portfolio, campaign


def build_ct(campaign_id: uuid.UUID, organization_id: uuid.UUID, **overrides) -> CampaignTimeModel:
    defaults = dict(
        campaign_id=campaign_id,
        organization_id=organization_id,
        is_active=True,
        next_execution=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    defaults.update(overrides)
    return CampaignTimeModel(**defaults)


class TestFindDueActive:
    async def test_returns_active_schedule_with_past_next_execution(self, db_session):
        org, _portfolio, campaign = await _setup_campaign(db_session)
        ct = build_ct(campaign.id, org.id, next_execution=datetime.now(timezone.utc) - timedelta(minutes=5))
        db_session.add(ct)
        await db_session.flush()

        repo = CampaignTimeRepository(db_session)
        due = await repo.find_due_active(datetime.now(timezone.utc))

        assert [d.id for d in due] == [ct.id]

    async def test_future_next_execution_is_not_due(self, db_session):
        org, _portfolio, campaign = await _setup_campaign(db_session)
        ct = build_ct(campaign.id, org.id, next_execution=datetime.now(timezone.utc) + timedelta(hours=1))
        db_session.add(ct)
        await db_session.flush()

        repo = CampaignTimeRepository(db_session)
        due = await repo.find_due_active(datetime.now(timezone.utc))

        assert due == []

    async def test_inactive_schedule_is_not_due(self, db_session):
        org, _portfolio, campaign = await _setup_campaign(db_session)
        ct = build_ct(campaign.id, org.id, is_active=False)
        db_session.add(ct)
        await db_session.flush()

        repo = CampaignTimeRepository(db_session)
        due = await repo.find_due_active(datetime.now(timezone.utc))

        assert due == []

    async def test_after_id_paginates_results(self, db_session):
        org, _portfolio, campaign_a = await _setup_campaign(db_session)
        _org2, _portfolio2, campaign_b = await _setup_campaign(db_session)
        ct_a = build_ct(campaign_a.id, org.id)
        ct_b = build_ct(campaign_b.id, org.id)
        db_session.add_all([ct_a, ct_b])
        await db_session.flush()

        repo = CampaignTimeRepository(db_session)
        now = datetime.now(timezone.utc)
        first_page = await repo.find_due_active(now, limit=1)
        assert len(first_page) == 1

        second_page = await repo.find_due_active(now, limit=1, after_id=first_page[-1].id)
        assert len(second_page) <= 1
        if second_page:
            assert second_page[0].id != first_page[0].id


class TestListActiveByOrg:
    async def test_joins_campaign_time_with_campaign(self, db_session):
        org, _portfolio, campaign = await _setup_campaign(db_session, name="Campaña activa")
        ct = build_ct(campaign.id, org.id)
        db_session.add(ct)
        await db_session.flush()

        repo = CampaignTimeRepository(db_session)
        rows = await repo.list_active_by_org(org.id)

        assert len(rows) == 1
        found_ct, found_campaign = rows[0]
        assert found_ct.id == ct.id
        assert found_campaign.name == "Campaña activa"

    async def test_inactive_schedule_is_excluded(self, db_session):
        org, _portfolio, campaign = await _setup_campaign(db_session)
        ct = build_ct(campaign.id, org.id, is_active=False)
        db_session.add(ct)
        await db_session.flush()

        repo = CampaignTimeRepository(db_session)
        rows = await repo.list_active_by_org(org.id)

        assert rows == []

    async def test_soft_deleted_campaign_is_excluded(self, db_session):
        org, _portfolio, campaign = await _setup_campaign(db_session)
        ct = build_ct(campaign.id, org.id)
        db_session.add(ct)
        await db_session.flush()

        campaign_repo = CampaignRepository(db_session)
        await campaign_repo.delete(campaign)

        repo = CampaignTimeRepository(db_session)
        rows = await repo.list_active_by_org(org.id)

        assert rows == []

    async def test_other_organization_schedules_are_excluded(self, db_session):
        org_a, _portfolio_a, campaign_a = await _setup_campaign(db_session)
        org_b, _portfolio_b, campaign_b = await _setup_campaign(db_session)
        db_session.add_all([build_ct(campaign_a.id, org_a.id), build_ct(campaign_b.id, org_b.id)])
        await db_session.flush()

        repo = CampaignTimeRepository(db_session)
        rows = await repo.list_active_by_org(org_a.id)

        assert len(rows) == 1
        assert rows[0][1].id == campaign_a.id


class TestDeactivateAndReschedule:
    async def test_deactivate_clears_next_execution_and_flags_inactive(self, db_session):
        org, _portfolio, campaign = await _setup_campaign(db_session)
        ct = build_ct(campaign.id, org.id)
        db_session.add(ct)
        await db_session.flush()

        repo = CampaignTimeRepository(db_session)
        updated = await repo.deactivate(ct)

        assert updated.is_active is False
        assert updated.next_execution is None

    async def test_reschedule_updates_next_execution_only(self, db_session):
        org, _portfolio, campaign = await _setup_campaign(db_session)
        ct = build_ct(campaign.id, org.id)
        db_session.add(ct)
        await db_session.flush()
        new_time = datetime.now(timezone.utc) + timedelta(days=1)

        repo = CampaignTimeRepository(db_session)
        updated = await repo.reschedule(ct, new_time)

        assert updated.is_active is True
        assert abs((updated.next_execution - new_time).total_seconds()) < 1


class TestGetByCampaign:
    async def test_returns_none_when_no_schedule_exists(self, db_session):
        _org, _portfolio, campaign = await _setup_campaign(db_session)
        repo = CampaignTimeRepository(db_session)
        assert await repo.get_by_campaign(campaign.id) is None

    async def test_returns_the_schedule_for_the_campaign(self, db_session):
        org, _portfolio, campaign = await _setup_campaign(db_session)
        ct = build_ct(campaign.id, org.id)
        db_session.add(ct)
        await db_session.flush()

        repo = CampaignTimeRepository(db_session)
        found = await repo.get_by_campaign(campaign.id)

        assert found is not None
        assert found.id == ct.id
