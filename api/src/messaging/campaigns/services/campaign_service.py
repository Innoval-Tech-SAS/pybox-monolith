import uuid
from datetime import datetime, timezone
from typing import Sequence

from fastapi import HTTPException, status

from billing.billing_status.services.billing_status_service import BillingStatusService
from messaging.campaigns.enums.campaign_enums import CampaignStatus, Periodicity
from messaging.campaigns.models.campaign_model import CampaignModel
from messaging.campaigns.models.campaign_time_model import CampaignTimeModel
from messaging.campaigns.repositories.campaign_repositories import CampaignRepository
from messaging.campaigns.repositories.campaign_time_repository import CampaignTimeRepository
from messaging.campaigns.schemas.campaign_schemas import CampaignCreateRequest, CampaignUpdateRequest
from messaging.campaigns.utils.calculate_next import calculate_next_execution


class CampaignService:

    def __init__(
        self,
        campaign_repo: CampaignRepository,
        ct_repo: CampaignTimeRepository,
        billing_status_service: BillingStatusService,
    ) -> None:
        self._repo = campaign_repo
        self._ct_repo = ct_repo
        self._billing_status_service = billing_status_service

    async def list_by_org(self, organization_id: uuid.UUID) -> Sequence[CampaignModel]:
        return await self._repo.list_by_organization(organization_id)

    async def get_by_id(self, campaign_id: uuid.UUID, organization_id: uuid.UUID) -> CampaignModel:
        campaign = await self._repo.get_by_id_and_org(campaign_id, organization_id)
        if campaign is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Campaña no encontrada")
        return campaign

    async def create(self, organization_id: uuid.UUID, data: CampaignCreateRequest) -> CampaignModel:
        campaign = CampaignModel(
            organization_id=organization_id,
            name=data.name,
            message=data.message,
            subject=data.subject,
            channel=data.channel,
            description=data.description,
            status=data.status,
            total_recipients=data.total_recipients,
            scheduled_at=data.scheduled_at,
            timezone=data.timezone,
            fallback=data.fallback,
            segment_id=data.segment_id,
            template_id=data.template_id,
            periodicity=data.periodicity,
            time_to_send=data.time_to_send,
            is_immediate=data.is_immediate,
        )
        return await self._repo.add(campaign)

    async def update(
        self,
        campaign_id: uuid.UUID,
        organization_id: uuid.UUID,
        data: CampaignUpdateRequest,
    ) -> CampaignModel:
        campaign = await self.get_by_id(campaign_id, organization_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(campaign, key, value)
        return await self._repo.update(campaign)

    async def delete(self, campaign_id: uuid.UUID, organization_id: uuid.UUID) -> None:
        campaign = await self.get_by_id(campaign_id, organization_id)
        await self._repo.delete(campaign)

    async def activate(self, campaign_id: uuid.UUID, organization_id: uuid.UUID) -> CampaignModel:
        if await self._billing_status_service.is_blocked(organization_id):
            raise HTTPException(
                status.HTTP_402_PAYMENT_REQUIRED,
                "Cuenta bloqueada por factura impaga. Realiza el pago para restablecer el acceso.",
            )

        campaign = await self.get_by_id(campaign_id, organization_id)

        if campaign.status not in (CampaignStatus.DRAFT, CampaignStatus.PAUSED):
            raise HTTPException(status.HTTP_409_CONFLICT, "Solo campañas en borrador o pausadas pueden activarse")

        if not campaign.segment_id:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "La campaña debe tener un segmento asignado")

        now = datetime.now(timezone.utc)
        next_execution: datetime

        if campaign.is_immediate:
            next_execution = now
        elif campaign.periodicity == Periodicity.ONCE and campaign.scheduled_at:
            next_execution = campaign.scheduled_at
        elif campaign.periodicity in (Periodicity.DAILY, Periodicity.WEEKLY, Periodicity.MONTHLY):
            if not campaign.time_to_send:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Campaña recurrente requiere time_to_send")
            next_execution = calculate_next_execution(
                periodicity=campaign.periodicity.value,
                time_to_send=campaign.time_to_send,
                timezone_iana=campaign.timezone,
                from_dt=now,
            )
        else:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Periodicidad no válida para activación")

        existing_ct = await self._ct_repo.get_by_campaign(campaign_id)
        if existing_ct:
            existing_ct.is_active = True
            existing_ct.next_execution = next_execution
            existing_ct.timezone_iana = campaign.timezone
            existing_ct.is_immediate = campaign.is_immediate
            existing_ct.time_to_send = campaign.time_to_send
            await self._ct_repo.update(existing_ct)
        else:
            ct = CampaignTimeModel(
                campaign_id=campaign_id,
                organization_id=organization_id,
                next_execution=next_execution,
                timezone_iana=campaign.timezone,
                is_active=True,
                is_immediate=campaign.is_immediate,
                time_to_send=campaign.time_to_send,
            )
            await self._ct_repo.add(ct)

        campaign.status = CampaignStatus.SCHEDULED
        return await self._repo.update(campaign)

    async def pause(self, campaign_id: uuid.UUID, organization_id: uuid.UUID) -> CampaignModel:
        campaign = await self.get_by_id(campaign_id, organization_id)
        if campaign.status != CampaignStatus.SCHEDULED:
            raise HTTPException(status.HTTP_409_CONFLICT, "Solo campañas programadas pueden pausarse")
        ct = await self._ct_repo.get_by_campaign(campaign_id)
        if ct:
            await self._ct_repo.deactivate(ct)
        campaign.status = CampaignStatus.PAUSED
        return await self._repo.update(campaign)
