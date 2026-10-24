"""Tests unitarios de `CampaignService` (ver campaign_service.py): validaciones de
creación/actualización y transiciones de estado permitidas. Todas las dependencias
(repos/servicios) van mockeadas con AsyncMock/MagicMock -- no toca la base de datos
real. `user_session` se arma con `make_user_session` (rol ADMIN, scope GLOBAL por
defecto, ver tests/conftest.py) para que `check_portfolio_org_access` no bloquee por
permisos y el test se enfoque en la lógica propia del servicio.
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from messaging.campaigns.enums.campaign_enums import CampaignStatus, Periodicity
from messaging.campaigns.models.campaign_time_model import CampaignTimeModel
from messaging.campaigns.schemas.campaign_schemas import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
)
from messaging.campaigns.services.campaign_service import CampaignService
from messaging.channels.enums.channel_enums import ChannelName
from tests.conftest import make_user_session


def make_service():
    campaign_repo = AsyncMock()
    ct_repo = AsyncMock()
    billing_status_service = AsyncMock()
    portfolio_repo = AsyncMock()
    template_repo = AsyncMock()
    channel_repo = AsyncMock()
    segment_repo = AsyncMock()
    recipient_count_service = AsyncMock()
    whatsapp_number_request_service = AsyncMock()
    ivr_flow_repo = AsyncMock()
    service = CampaignService(
        campaign_repo,
        ct_repo,
        billing_status_service,
        portfolio_repo,
        template_repo,
        channel_repo,
        segment_repo,
        recipient_count_service,
        whatsapp_number_request_service,
        ivr_flow_repo,
    )
    return (
        service,
        campaign_repo,
        ct_repo,
        billing_status_service,
        portfolio_repo,
        template_repo,
        channel_repo,
        segment_repo,
        whatsapp_number_request_service,
        ivr_flow_repo,
    )


def make_portfolio(**overrides) -> MagicMock:
    defaults = dict(id=uuid.uuid4(), organization_id=uuid.uuid4())
    defaults.update(overrides)
    portfolio = MagicMock()
    for key, value in defaults.items():
        setattr(portfolio, key, value)
    return portfolio


def make_campaign(**overrides) -> MagicMock:
    defaults = dict(
        id=uuid.uuid4(),
        portfolio_id=uuid.uuid4(),
        status=CampaignStatus.DRAFT,
        segment_id=uuid.uuid4(),
        channel_id=uuid.uuid4(),
        template_id=None,
        message="hola",
        subject=None,
        periodicity=None,
        scheduled_at=None,
        time_to_send=None,
        timezone="UTC",
        days_of_week=None,
        day_of_month=None,
        is_immediate=False,
    )
    defaults.update(overrides)
    campaign = MagicMock()
    for key, value in defaults.items():
        setattr(campaign, key, value)
    return campaign


def make_channel(name: ChannelName = ChannelName.SMS) -> MagicMock:
    channel = MagicMock()
    channel.name = name
    return channel


def create_payload(**overrides) -> CampaignCreateRequest:
    defaults = dict(
        name="Campaña de prueba", message="hola {{nombre}}", channel_id=uuid.uuid4()
    )
    defaults.update(overrides)
    return CampaignCreateRequest(**defaults)


def admin_session():
    return make_user_session()


# ---------------------------------------------------------------------------
# Validaciones de programación / días / día del mes
# ---------------------------------------------------------------------------
class TestScheduleValidation:
    def test_sunday_in_days_of_week_is_rejected(self):
        service, *_ = make_service()
        with pytest.raises(HTTPException) as exc_info:
            service._assert_valid_days_of_week([0, 1])
        assert exc_info.value.status_code == 422

    def test_valid_weekdays_are_accepted(self):
        service, *_ = make_service()
        service._assert_valid_days_of_week([1, 3, 5])  # no debe lanzar

    def test_none_days_of_week_is_accepted(self):
        service, *_ = make_service()
        service._assert_valid_days_of_week(None)

    @pytest.mark.parametrize("day", [0, 32, -1])
    def test_day_of_month_out_of_range_is_rejected(self, day):
        service, *_ = make_service()
        with pytest.raises(HTTPException) as exc_info:
            service._assert_valid_day_of_month(day)
        assert exc_info.value.status_code == 422

    def test_day_of_month_31_is_accepted_as_last_day_marker(self):
        service, *_ = make_service()
        service._assert_valid_day_of_month(31)  # no debe lanzar

    def test_immediate_skips_all_scheduling_validation(self):
        service, *_ = make_service()
        service._validate_scheduling_input(
            True, None, None, None, None
        )  # no debe lanzar

    def test_once_without_scheduled_at_is_rejected(self):
        service, *_ = make_service()
        with pytest.raises(HTTPException) as exc_info:
            service._validate_scheduling_input(
                False, Periodicity.ONCE, None, "08:00", None
            )
        assert exc_info.value.status_code == 422

    def test_once_with_scheduled_at_and_time_is_accepted(self):
        service, *_ = make_service()
        service._validate_scheduling_input(
            False, Periodicity.ONCE, datetime.now(timezone.utc), "08:00", None
        )

    def test_recurring_without_time_to_send_is_rejected(self):
        service, *_ = make_service()
        with pytest.raises(HTTPException) as exc_info:
            service._validate_scheduling_input(
                False, Periodicity.DAILY, None, None, None
            )
        assert exc_info.value.status_code == 422

    def test_weekly_without_days_of_week_is_rejected(self):
        service, *_ = make_service()
        with pytest.raises(HTTPException) as exc_info:
            service._validate_scheduling_input(
                False, Periodicity.WEEKLY, None, "08:00", None
            )
        assert exc_info.value.status_code == 422

    def test_weekly_with_days_of_week_is_accepted(self):
        service, *_ = make_service()
        service._validate_scheduling_input(
            False, Periodicity.WEEKLY, None, "08:00", [1, 2]
        )

    def test_monthly_with_time_to_send_is_accepted(self):
        service, *_ = make_service()
        service._validate_scheduling_input(
            False, Periodicity.MONTHLY, None, "08:00", None
        )


# ---------------------------------------------------------------------------
# assert_template_channel_compatibility / _validate_channel_content
# ---------------------------------------------------------------------------
class TestTemplateChannelCompatibility:
    async def test_missing_template_raises_404(self):
        service, _cr, _ct, _b, _p, template_repo, channel_repo, _s, _w, _ivr = (
            make_service()
        )
        template_repo.get_by_id_and_portfolio = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.assert_template_channel_compatibility(
                uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
            )
        assert exc_info.value.status_code == 404
        channel_repo.get_by_id.assert_not_awaited()

    async def test_missing_channel_raises_404(self):
        service, _cr, _ct, _b, _p, template_repo, channel_repo, _s, _w, _ivr = (
            make_service()
        )
        template_repo.get_by_id_and_portfolio = AsyncMock(
            return_value=MagicMock(channel=ChannelName.SMS)
        )
        channel_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.assert_template_channel_compatibility(
                uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
            )
        assert exc_info.value.status_code == 404

    async def test_mismatched_channel_raises_422(self):
        service, _cr, _ct, _b, _p, template_repo, channel_repo, _s, _w, _ivr = (
            make_service()
        )
        template_repo.get_by_id_and_portfolio = AsyncMock(
            return_value=MagicMock(channel=ChannelName.EMAIL)
        )
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))

        with pytest.raises(HTTPException) as exc_info:
            await service.assert_template_channel_compatibility(
                uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
            )
        assert exc_info.value.status_code == 422

    async def test_matching_channel_does_not_raise(self):
        service, _cr, _ct, _b, _p, template_repo, channel_repo, _s, _w, _ivr = (
            make_service()
        )
        template_repo.get_by_id_and_portfolio = AsyncMock(
            return_value=MagicMock(channel=ChannelName.SMS)
        )
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))

        await service.assert_template_channel_compatibility(
            uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        )


class TestValidateChannelContent:
    async def test_whatsapp_without_template_id_is_rejected(self):
        service, *_r, channel_repo, _s, _w, _ivr = make_service()
        channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.WHATSAPP)
        )

        with pytest.raises(HTTPException) as exc_info:
            await service._validate_channel_content(uuid.uuid4(), None, None)
        assert exc_info.value.status_code == 422

    async def test_whatsapp_with_message_is_rejected(self):
        service, *_r, channel_repo, _s, _w, _ivr = make_service()
        channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.WHATSAPP)
        )

        with pytest.raises(HTTPException) as exc_info:
            await service._validate_channel_content(
                uuid.uuid4(), uuid.uuid4(), "no debería llevar message"
            )
        assert exc_info.value.status_code == 422

    async def test_whatsapp_with_only_template_id_is_accepted(self):
        service, *_r, channel_repo, _s, _w, _ivr = make_service()
        channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.WHATSAPP)
        )

        await service._validate_channel_content(uuid.uuid4(), uuid.uuid4(), None)

    async def test_non_whatsapp_without_message_is_rejected(self):
        service, *_r, channel_repo, _s, _w, _ivr = make_service()
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))

        with pytest.raises(HTTPException) as exc_info:
            await service._validate_channel_content(uuid.uuid4(), None, None)
        assert exc_info.value.status_code == 422

    async def test_channel_not_found_raises_404(self):
        service, *_r, channel_repo, _s, _w, _ivr = make_service()
        channel_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service._validate_channel_content(uuid.uuid4(), None, "mensaje")
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# create()
# ---------------------------------------------------------------------------
class TestCreate:
    async def test_creates_campaign_and_persists_via_repo(self):
        (
            service,
            campaign_repo,
            _ct,
            _b,
            portfolio_repo,
            _t,
            channel_repo,
            _s,
            whatsapp_svc,
            _ivr,
        ) = make_service()
        portfolio = make_portfolio()
        portfolio_repo.get_by_id = AsyncMock(return_value=portfolio)
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))
        campaign_repo.add = AsyncMock(side_effect=lambda c: c)

        payload = create_payload()
        result = await service.create(portfolio.id, payload, admin_session())

        assert result.name == payload.name
        assert result.portfolio_id == portfolio.id
        campaign_repo.add.assert_awaited_once()
        whatsapp_svc.ensure_number_available.assert_not_awaited()

    async def test_whatsapp_channel_triggers_number_request_without_blocking(self):
        (
            service,
            campaign_repo,
            _ct,
            _b,
            portfolio_repo,
            template_repo,
            channel_repo,
            _s,
            whatsapp_svc,
            _ivr,
        ) = make_service()
        portfolio = make_portfolio()
        portfolio_repo.get_by_id = AsyncMock(return_value=portfolio)
        template_repo.get_by_id_and_portfolio = AsyncMock(
            return_value=MagicMock(channel=ChannelName.WHATSAPP)
        )
        channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.WHATSAPP)
        )
        whatsapp_svc.ensure_number_available = AsyncMock(
            return_value=False
        )  # sin número aún
        campaign_repo.add = AsyncMock(side_effect=lambda c: c)

        payload = create_payload(message=None, template_id=uuid.uuid4())
        result = await service.create(portfolio.id, payload, admin_session())

        # No bloquea la creación aunque no haya número todavía (queda en DRAFT).
        assert result is not None
        whatsapp_svc.ensure_number_available.assert_awaited_once()

    async def test_invalid_days_of_week_prevents_creation(self):
        service, campaign_repo, *_ = make_service()
        payload = create_payload(
            periodicity=Periodicity.WEEKLY, time_to_send="08:00", days_of_week=[0]
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.create(uuid.uuid4(), payload, admin_session())
        assert exc_info.value.status_code == 422
        campaign_repo.add.assert_not_awaited()

    async def test_segment_not_in_portfolio_prevents_creation(self):
        (
            service,
            campaign_repo,
            _ct,
            _b,
            portfolio_repo,
            _t,
            channel_repo,
            segment_repo,
            _w,
            _ivr,
        ) = make_service()
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))
        segment_repo.get_by_id_and_portfolio = AsyncMock(return_value=None)

        payload = create_payload(segment_id=uuid.uuid4())
        with pytest.raises(HTTPException) as exc_info:
            await service.create(uuid.uuid4(), payload, admin_session())
        assert exc_info.value.status_code == 404
        campaign_repo.add.assert_not_awaited()


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------
class TestUpdate:
    async def test_updates_fields_and_persists(self):
        (
            service,
            campaign_repo,
            ct_repo,
            _b,
            portfolio_repo,
            _t,
            channel_repo,
            _s,
            _w,
            _ivr,
        ) = make_service()
        campaign = make_campaign(status=CampaignStatus.DRAFT)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))
        campaign_repo.update = AsyncMock(side_effect=lambda c: c)

        result = await service.update(
            campaign.id,
            campaign.portfolio_id,
            CampaignUpdateRequest(name="Nuevo nombre"),
            admin_session(),
        )

        assert result.name == "Nuevo nombre"
        campaign_repo.update.assert_awaited_once()

    async def test_scheduled_campaign_resyncs_schedule_on_update(self):
        (
            service,
            campaign_repo,
            ct_repo,
            _b,
            portfolio_repo,
            _t,
            channel_repo,
            _s,
            _w,
            _ivr,
        ) = make_service()
        campaign = make_campaign(
            status=CampaignStatus.SCHEDULED,
            periodicity=Periodicity.DAILY,
            time_to_send="08:00",
        )
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))
        ct_repo.get_by_campaign = AsyncMock(return_value=None)
        ct_repo.add = AsyncMock()
        campaign_repo.update = AsyncMock(side_effect=lambda c: c)

        await service.update(
            campaign.id,
            campaign.portfolio_id,
            CampaignUpdateRequest(name="X"),
            admin_session(),
        )

        ct_repo.add.assert_awaited_once()  # se creó la programación porque no existía

    async def test_draft_campaign_does_not_resync_schedule(self):
        (
            service,
            campaign_repo,
            ct_repo,
            _b,
            portfolio_repo,
            _t,
            channel_repo,
            _s,
            _w,
            _ivr,
        ) = make_service()
        campaign = make_campaign(status=CampaignStatus.DRAFT)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))
        campaign_repo.update = AsyncMock(side_effect=lambda c: c)

        await service.update(
            campaign.id,
            campaign.portfolio_id,
            CampaignUpdateRequest(name="X"),
            admin_session(),
        )

        ct_repo.get_by_campaign.assert_not_awaited()

    async def test_campaign_not_found_raises_404(self):
        service, campaign_repo, *_ = make_service()
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await service.update(
                uuid.uuid4(),
                uuid.uuid4(),
                CampaignUpdateRequest(name="X"),
                admin_session(),
            )
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# activate()
# ---------------------------------------------------------------------------
class TestActivate:
    async def test_blocked_billing_raises_402_before_touching_campaign(self):
        service, campaign_repo, _ct, billing, portfolio_repo, *_ = make_service()
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=True)

        with pytest.raises(HTTPException) as exc_info:
            await service.activate(uuid.uuid4(), uuid.uuid4(), admin_session())
        assert exc_info.value.status_code == 402
        campaign_repo.get_by_id_and_portfolio.assert_not_awaited()

    async def test_completed_campaign_cannot_be_activated(self):
        service, campaign_repo, _ct, billing, portfolio_repo, *_ = make_service()
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=False)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(
            return_value=make_campaign(status=CampaignStatus.COMPLETED)
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.activate(uuid.uuid4(), uuid.uuid4(), admin_session())
        assert exc_info.value.status_code == 409

    async def test_draft_campaign_can_be_activated(self):
        (
            service,
            campaign_repo,
            ct_repo,
            billing,
            portfolio_repo,
            _t,
            channel_repo,
            _s,
            _w,
            _ivr,
        ) = make_service()
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=False)
        campaign = make_campaign(status=CampaignStatus.DRAFT, is_immediate=True)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))
        ct_repo.get_by_campaign = AsyncMock(return_value=None)
        ct_repo.add = AsyncMock()
        campaign_repo.update = AsyncMock(side_effect=lambda c: c)

        result = await service.activate(
            campaign.id, campaign.portfolio_id, admin_session()
        )

        assert result.status == CampaignStatus.SCHEDULED
        campaign_repo.update.assert_awaited_once()

    async def test_paused_campaign_can_be_activated(self):
        (
            service,
            campaign_repo,
            ct_repo,
            billing,
            portfolio_repo,
            _t,
            channel_repo,
            _s,
            _w,
            _ivr,
        ) = make_service()
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=False)
        campaign = make_campaign(status=CampaignStatus.PAUSED, is_immediate=True)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))
        ct_repo.get_by_campaign = AsyncMock(return_value=None)
        ct_repo.add = AsyncMock()
        campaign_repo.update = AsyncMock(side_effect=lambda c: c)

        result = await service.activate(
            campaign.id, campaign.portfolio_id, admin_session()
        )
        assert result.status == CampaignStatus.SCHEDULED

    async def test_activation_without_segment_is_rejected(self):
        service, campaign_repo, _ct, billing, portfolio_repo, *_ = make_service()
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=False)
        campaign = make_campaign(status=CampaignStatus.DRAFT, segment_id=None)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)

        with pytest.raises(HTTPException) as exc_info:
            await service.activate(campaign.id, campaign.portfolio_id, admin_session())
        assert exc_info.value.status_code == 422

    async def test_whatsapp_without_number_is_rejected(self):
        (
            service,
            campaign_repo,
            _ct,
            billing,
            portfolio_repo,
            _t,
            channel_repo,
            _s,
            whatsapp_svc,
            _ivr,
        ) = make_service()
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=False)
        campaign = make_campaign(status=CampaignStatus.DRAFT, is_immediate=True)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.WHATSAPP)
        )
        whatsapp_svc.ensure_number_available = AsyncMock(return_value=False)

        with pytest.raises(HTTPException) as exc_info:
            await service.activate(campaign.id, campaign.portfolio_id, admin_session())
        assert exc_info.value.status_code == 422

    async def test_whatsapp_with_number_can_be_activated(self):
        (
            service,
            campaign_repo,
            ct_repo,
            billing,
            portfolio_repo,
            _t,
            channel_repo,
            _s,
            whatsapp_svc,
            _ivr,
        ) = make_service()
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=False)
        campaign = make_campaign(status=CampaignStatus.DRAFT, is_immediate=True)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        channel_repo.get_by_id = AsyncMock(
            return_value=make_channel(ChannelName.WHATSAPP)
        )
        whatsapp_svc.ensure_number_available = AsyncMock(return_value=True)
        ct_repo.get_by_campaign = AsyncMock(return_value=None)
        ct_repo.add = AsyncMock()
        campaign_repo.update = AsyncMock(side_effect=lambda c: c)

        result = await service.activate(
            campaign.id, campaign.portfolio_id, admin_session()
        )
        assert result.status == CampaignStatus.SCHEDULED

    async def test_recurring_without_time_to_send_raises_422_during_sync(self):
        service, campaign_repo, _ct, billing, portfolio_repo, _t, channel_repo, *_ = (
            make_service()
        )
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=False)
        campaign = make_campaign(
            status=CampaignStatus.DRAFT,
            is_immediate=False,
            periodicity=Periodicity.DAILY,
            time_to_send=None,
        )
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))

        with pytest.raises(HTTPException) as exc_info:
            await service.activate(campaign.id, campaign.portfolio_id, admin_session())
        assert exc_info.value.status_code == 422

    async def test_invalid_periodicity_for_activation_raises_422(self):
        service, campaign_repo, _ct, billing, portfolio_repo, _t, channel_repo, *_ = (
            make_service()
        )
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=False)
        # periodicity=None y is_immediate=False no matchea ninguna rama válida de _sync_schedule.
        campaign = make_campaign(
            status=CampaignStatus.DRAFT, is_immediate=False, periodicity=None
        )
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))

        with pytest.raises(HTTPException) as exc_info:
            await service.activate(campaign.id, campaign.portfolio_id, admin_session())
        assert exc_info.value.status_code == 422

    async def test_existing_schedule_is_updated_not_duplicated(self):
        (
            service,
            campaign_repo,
            ct_repo,
            billing,
            portfolio_repo,
            _t,
            channel_repo,
            *_,
        ) = make_service()
        portfolio_repo.get_by_id = AsyncMock(return_value=make_portfolio())
        billing.is_blocked = AsyncMock(return_value=False)
        campaign = make_campaign(status=CampaignStatus.PAUSED, is_immediate=True)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        channel_repo.get_by_id = AsyncMock(return_value=make_channel(ChannelName.SMS))
        existing_ct = MagicMock(spec=CampaignTimeModel)
        ct_repo.get_by_campaign = AsyncMock(return_value=existing_ct)
        ct_repo.update = AsyncMock()
        ct_repo.add = AsyncMock()
        campaign_repo.update = AsyncMock(side_effect=lambda c: c)

        await service.activate(campaign.id, campaign.portfolio_id, admin_session())

        ct_repo.update.assert_awaited_once()
        ct_repo.add.assert_not_awaited()
        assert existing_ct.is_active is True


# ---------------------------------------------------------------------------
# pause()
# ---------------------------------------------------------------------------
class TestPause:
    async def test_scheduled_campaign_can_be_paused_and_deactivates_schedule(self):
        service, campaign_repo, ct_repo, *_ = make_service()
        campaign = make_campaign(status=CampaignStatus.SCHEDULED)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        ct = MagicMock(spec=CampaignTimeModel)
        ct_repo.get_by_campaign = AsyncMock(return_value=ct)
        ct_repo.deactivate = AsyncMock()
        campaign_repo.update = AsyncMock(side_effect=lambda c: c)

        result = await service.pause(
            campaign.id, campaign.portfolio_id, admin_session()
        )

        assert result.status == CampaignStatus.PAUSED
        ct_repo.deactivate.assert_awaited_once_with(ct)

    async def test_draft_campaign_cannot_be_paused(self):
        service, campaign_repo, ct_repo, *_ = make_service()
        campaign = make_campaign(status=CampaignStatus.DRAFT)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)

        with pytest.raises(HTTPException) as exc_info:
            await service.pause(campaign.id, campaign.portfolio_id, admin_session())
        assert exc_info.value.status_code == 409
        ct_repo.deactivate.assert_not_awaited()

    async def test_pause_without_existing_schedule_does_not_call_deactivate(self):
        service, campaign_repo, ct_repo, *_ = make_service()
        campaign = make_campaign(status=CampaignStatus.SCHEDULED)
        campaign_repo.get_by_id_and_portfolio = AsyncMock(return_value=campaign)
        ct_repo.get_by_campaign = AsyncMock(return_value=None)
        campaign_repo.update = AsyncMock(side_effect=lambda c: c)

        result = await service.pause(
            campaign.id, campaign.portfolio_id, admin_session()
        )

        assert result.status == CampaignStatus.PAUSED
        ct_repo.deactivate.assert_not_awaited()
