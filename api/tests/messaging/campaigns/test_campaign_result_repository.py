"""Tests de `CampaignResultRepository` contra la base de datos real (sin mocks):
registra el resultado agregado de un envío (ver `_execute_campaign_once` en
automation_service.py, que lo llama dentro de un savepoint). Se prueba que
persiste los conteos exactos y que `campaign_time_id` -- opcional, puede venir
`None` para un envío manual sin programación asociada -- se respeta.
"""

from messaging.campaigns.models.campaign_time_model import CampaignTimeModel
from messaging.campaigns.repository.campaign_result_repository import CampaignResultRepository
from tests.messaging.campaigns.conftest import build_campaign, get_channel_id
from tests.receivables.conftest import build_organization, build_portfolio


async def _setup_campaign(db_session):
    org = build_organization()
    db_session.add(org)
    await db_session.flush()
    portfolio = build_portfolio(org.id)
    db_session.add(portfolio)
    await db_session.flush()
    channel_id = await get_channel_id(db_session)
    campaign = build_campaign(portfolio.id, channel_id)
    db_session.add(campaign)
    await db_session.flush()
    return org, campaign


class TestCreate:
    async def test_persists_exact_counts_and_sets_sent_at(self, db_session):
        org, campaign = await _setup_campaign(db_session)

        repo = CampaignResultRepository(db_session)
        result = await repo.create(
            campaign_id=campaign.id,
            organization_id=org.id,
            campaign_time_id=None,
            total_sent=100,
            success_count=87,
            failure_count=13,
            unique_customers=95,
        )

        assert result.id is not None
        assert result.total_sent == 100
        assert result.success_count == 87
        assert result.failure_count == 13
        assert result.unique_customers == 95
        assert result.sent_at is not None
        assert result.campaign_time_id is None
        assert result.sending_id is None

    async def test_persists_with_optional_campaign_time_id_and_sending_id(self, db_session):
        org, campaign = await _setup_campaign(db_session)
        ct = CampaignTimeModel(campaign_id=campaign.id, organization_id=org.id, is_active=True)
        db_session.add(ct)
        await db_session.flush()

        repo = CampaignResultRepository(db_session)
        result = await repo.create(
            campaign_id=campaign.id,
            organization_id=org.id,
            campaign_time_id=ct.id,
            total_sent=10,
            success_count=10,
            failure_count=0,
            unique_customers=10,
            sending_id="sending-abc",
        )

        assert result.campaign_time_id == ct.id
        assert result.sending_id == "sending-abc"

    async def test_multiple_results_for_same_campaign_are_independent_rows(self, db_session):
        """Cada tick recurrente crea un nuevo resultado -- no debe pisar el anterior
        (no hay upsert por campaña, es historial)."""
        org, campaign = await _setup_campaign(db_session)
        repo = CampaignResultRepository(db_session)

        first = await repo.create(
            campaign_id=campaign.id, organization_id=org.id, campaign_time_id=None,
            total_sent=5, success_count=5, failure_count=0, unique_customers=5,
        )
        second = await repo.create(
            campaign_id=campaign.id, organization_id=org.id, campaign_time_id=None,
            total_sent=8, success_count=6, failure_count=2, unique_customers=8,
        )

        assert first.id != second.id
        assert first.total_sent == 5
        assert second.total_sent == 8
